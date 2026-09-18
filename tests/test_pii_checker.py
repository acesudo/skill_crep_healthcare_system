"""Unit tests for PiiValidator.
"""

import pytest
from src.data_generation.pii_checker import PiiValidator


def test_pii_clean_text():
    clean_text = "Good morning, I need a refill of my Metformin 500mg sent to CVS."
    findings = PiiValidator.check_text(clean_text)
    assert len(findings) == 0


def test_pii_detects_real_email():
    text_with_email = "Please send my lab results to john.doe@realclinic.org right away."
    findings = PiiValidator.check_text(text_with_email)
    assert len(findings) == 1
    assert findings[0][0] == "EMAIL"


def test_pii_detects_ssn():
    text_with_ssn = "My social security number for identification is 123-45-6789."
    findings = PiiValidator.check_text(text_with_ssn)
    assert len(findings) == 1
    assert findings[0][0] == "SSN"


def test_pii_detects_mrn():
    text_with_mrn = "Please update records for MRN 98234123."
    findings = PiiValidator.check_text(text_with_mrn)
    assert len(findings) == 1
    assert findings[0][0] == "MRN"
