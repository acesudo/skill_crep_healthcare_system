"""FastAPI entrypoint and application factory for PS-1.
Configures modern lifespan management, request correlation tracking, CORS,
structured non-PHI logging, and consistent exception formatting.
"""

from contextlib import asynccontextmanager
import logging
import time
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.config import get_settings
from src.api.routes.batch import router as batch_router
from src.api.routes.health import router as health_router
from src.api.routes.prediction import router as prediction_router
from src.api.schemas import ErrorResponse, StatusEnum
from src.api.services.inference_service import InferenceService

# Configure structured application logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)
logger = logging.getLogger("triage_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan event handler: loads ML artifacts during startup and cleans up on shutdown."""
    settings = get_settings()
    logger.info("Initializing PS-1 Triage API...")
    logger.info("Configuration: env=%s, expected_version=%s, threshold=%.2f",
                settings.app_env, settings.model_version, settings.confidence_threshold)

    try:
        # Load serialized Section 9 ML artifacts once into memory
        inference_service = InferenceService.from_artifacts(
            base_dir=settings.model_base_path,
            version=settings.model_version,
            threshold=settings.confidence_threshold,
            max_message_length=settings.max_message_length,
        )

        # Verify loaded version matches configuration
        loaded_version = str(inference_service.metadata.get("model_version"))
        if loaded_version != settings.model_version:
            logger.warning(
                "Version mismatch: loaded '%s' but settings configured '%s'",
                loaded_version, settings.model_version
            )

        app.state.inference_service = inference_service
        logger.info("ML inference engine loaded successfully. Model Version: %s", loaded_version)
    except Exception as exc:
        logger.critical("FATAL: Failed to load ML model artifacts: %s", exc, exc_info=True)
        app.state.inference_service = None

    yield

    logger.info("Shutting down PS-1 Triage API...")


app = FastAPI(
    title="Patient Message Triage & Urgency Classifier API",
    description=(
        "Operational triage and prioritization API for healthcare patient-support communications.\n\n"
        "**HEALTHCARE SAFETY NOTICE:** This system functions strictly as an operational switchboard "
        "and administrative triage assistant. It does NOT diagnose medical conditions, recommend treatments, "
        "prescribe medications, or replace emergency clinical triage."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

settings = get_settings()

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 2. Request Correlation ID & Latency Logging Middleware
@app.middleware("http")
async def correlation_and_logging_middleware(request: Request, call_next):
    """Attaches traceable request ID and logs operational performance without logging message PHI."""
    request_id = request.headers.get("X-Request-ID") or f"REQ-{uuid4().hex[:12]}"
    request.state.request_id = request_id

    start_time = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        logger.error(
            "Unhandled server error: method=%s path=%s duration=%.2fms request_id=%s error=%s",
            request.method, request.url.path, duration_ms, request_id, str(exc),
        )
        raise exc

    duration_ms = (time.perf_counter() - start_time) * 1000.0
    response.headers["X-Request-ID"] = request_id

    # Operational audit log: Never log raw message_text or client bodies to protect patient confidentiality
    logger.info(
        "Handled request: method=%s path=%s status=%d duration=%.2fms request_id=%s",
        request.method, request.url.path, response.status_code, duration_ms, request_id,
    )
    return response


# 3. Global Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Formats validation errors into standardized structured error response."""
    request_id = getattr(request.state, "request_id", None)
    error_details = []
    for err in exc.errors():
        field_loc = " -> ".join(str(loc) for loc in err.get("loc", []))
        msg = err.get("msg", "Invalid value")
        error_details.append(f"Field '{field_loc}': {msg}")

    detail_str = "; ".join(error_details)
    logger.warning("Validation failure: path=%s request_id=%s detail=%s",
                   request.url.path, request_id, detail_str)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=ErrorResponse(
            status=StatusEnum.INVALID_INPUT,
            detail=f"Request validation failed: {detail_str}",
            request_id=request_id,
        ).model_dump(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Consistent formatting for HTTP exceptions."""
    request_id = getattr(request.state, "request_id", None)
    status_enum = (
        StatusEnum.INVALID_INPUT
        if exc.status_code in (400, 413, 422)
        else StatusEnum.PROCESSING_FAILURE
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            status=status_enum,
            detail=str(exc.detail),
            request_id=request_id,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Failsafe handler for unexpected exceptions, avoiding internal stack trace leakage."""
    request_id = getattr(request.state, "request_id", None)
    logger.exception("Unexpected internal exception: request_id=%s", request_id)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status=StatusEnum.PROCESSING_FAILURE,
            detail="An internal server error occurred while processing the request.",
            request_id=request_id,
        ).model_dump(),
    )


# 4. Mount Route Controllers
app.include_router(health_router)
app.include_router(prediction_router)
app.include_router(batch_router)
