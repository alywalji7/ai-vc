"""
Tests for the document generator module.
"""

import os
import pytest
from datetime import datetime
from pathlib import Path

from app.core.document_generator import DocumentGenerator
from app.models.schemas import DocumentType

# Create test output directory
TEST_OUTPUT_DIR = "test_output"
os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)


@pytest.fixture
def document_generator():
    """Fixture for the document generator."""
    generator = DocumentGenerator()
    # Override output directory for tests
    generator.OUTPUT_DIR = Path(TEST_OUTPUT_DIR)
    return generator


@pytest.fixture
def safe_details():
    """Fixture for SAFE document details."""
    return {
        "investment_amount": 500000,
        "valuation_cap": 8000000,
        "discount_rate": 20,
        "company_name": "Test Company Inc.",
        "investor_name": "Test Investor LLC",
        "effective_date": datetime.now().strftime("%Y-%m-%d"),
        "company_signatory_name": "Test CEO",
        "company_signatory_title": "CEO",
        "investor_signatory_name": "Test Investor",
        "investor_signatory_title": "Managing Partner"
    }


def test_generate_safe_document(document_generator, safe_details):
    """Test generating a SAFE document."""
    # Generate document
    document_path = document_generator.generate_safe_document(safe_details)
    
    # Verify document was created
    assert os.path.exists(document_path)
    assert document_path.endswith(".docx")
    assert DocumentType.SERIES_SEED_SAFE.value in document_path


def test_get_template_path(document_generator):
    """Test getting template path."""
    # Get template path for SAFE document
    template_path = document_generator.get_template_path(DocumentType.SERIES_SEED_SAFE)
    
    # Verify template path
    assert template_path.exists()
    assert template_path.name == "SeriesSeed-SAFE-Template.docx"


def test_invalid_document_type(document_generator):
    """Test handling invalid document type."""
    # Create an invalid document type
    class InvalidDocumentType:
        value = "invalid"
    
    # Verify ValueError is raised
    with pytest.raises(ValueError):
        document_generator.get_template_path(InvalidDocumentType)