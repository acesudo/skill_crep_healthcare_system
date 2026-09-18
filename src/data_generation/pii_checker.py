"""PII validation and safety checks for synthetic healthcare message datasets.
"""

import re
from typing import Dict, List, Tuple


class PiiValidator:
    """Detects presence of unintended Personal Identifiable Information (PII)
    or real Protected Health Information (PHI) in synthetic messages.
    """

    # Compiled patterns for PII inspection
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
    # Matches real US phone formats, excluding synthetic 555-01xx fictitious exchanges
    PHONE_PATTERN = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b")
    SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
    MRN_PATTERN = re.compile(r"\b(?:MRN|mrn|Medical Record #?)[:\s]*\d{6,10}\b", re.IGNORECASE)
    STREET_ADDRESS_PATTERN = re.compile(r"\b\d{1,5}\s+(?:[A-Za-z]+\s+){1,3}(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b", re.IGNORECASE)

    @classmethod
    def is_synthetic_safe_phone(cls, match_text: str) -> bool:
        """Allows standard fictional 555-01XX exchanges (RFC 2606 style numbers)."""
        clean = re.sub(r"[^\d]", "", match_text)
        return "55501" in clean

    @classmethod
    def check_text(cls, text: str) -> List[Tuple[str, str]]:
        """Scans text and returns list of (violation_type, matched_string)."""
        if not text or not isinstance(text, str):
            return []
        violations = []

        # Email check
        for email in cls.EMAIL_PATTERN.findall(text):
            if not email.endswith("@example.com") and not email.endswith("@synthetic.test"):
                violations.append(("EMAIL", email))

        # SSN check
        for ssn in cls.SSN_PATTERN.findall(text):
            violations.append(("SSN", ssn))

        # Phone check
        for phone in cls.PHONE_PATTERN.findall(text):
            if not cls.is_synthetic_safe_phone(phone):
                violations.append(("PHONE", phone))

        # MRN check
        for mrn in cls.MRN_PATTERN.findall(text):
            violations.append(("MRN", mrn))

        # Street address check
        for addr in cls.STREET_ADDRESS_PATTERN.findall(text):
            violations.append(("STREET_ADDRESS", addr))

        return violations

    @classmethod
    def validate_dataset(cls, messages: List[Dict[str, str]]) -> Dict[str, any]:
        """Audits an entire list of message records for PII violations."""
        total_violations = 0
        violation_records = []

        for record in messages:
            msg_id = record.get("message_id", "UNKNOWN")
            text = record.get("message_text", "")
            findings = cls.check_text(text)
            if findings:
                total_violations += len(findings)
                violation_records.append({
                    "message_id": msg_id,
                    "findings": findings,
                    "text_snippet": text[:80] + "...",
                })

        return {
            "passed": total_violations == 0,
            "total_violations": total_violations,
            "flagged_record_count": len(violation_records),
            "flagged_records": violation_records,
        }
