"""
Document generation functionality for the Term Sheet Generator service.

This module is responsible for filling NVCA model document templates
using the docxtpl library.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from docxtpl import DocxTemplate

from ..models.schemas import DocumentType

logger = logging.getLogger(__name__)

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates" / "nvca"
OUTPUT_DIR = BASE_DIR / "output"


class DocumentGenerator:
    """
    Generator for legal documents based on NVCA templates.
    """
    
    def __init__(self):
        """Initialize the document generator."""
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Map document types to template files
        self.template_map = {
            DocumentType.SERIES_SEED_SAFE: "SeriesSeed-SAFE-Template.docx",
            DocumentType.SERIES_A_TERM_SHEET: "SeriesA-TermSheet-Template.docx",
            # Add other document templates as needed
        }
    
    def get_template_path(self, document_type: DocumentType) -> Path:
        """
        Get the template file path for a given document type.
        
        Args:
            document_type: Type of document to generate
            
        Returns:
            Path to the template file
            
        Raises:
            ValueError: If the template for the document type is not found
        """
        if document_type not in self.template_map:
            raise ValueError(f"No template found for document type: {document_type}")
        
        template_file = self.template_map[document_type]
        template_path = TEMPLATES_DIR / template_file
        
        if not template_path.exists():
            raise ValueError(f"Template file not found: {template_path}")
            
        return template_path
    
    def generate_document(self, document_type: DocumentType, context: Dict[str, Any]) -> str:
        """
        Generate a document by filling a template with the provided context.
        
        Args:
            document_type: Type of document to generate
            context: Dictionary of values to fill into the template
            
        Returns:
            Path to the generated document
            
        Raises:
            ValueError: If document generation fails
        """
        try:
            template_path = self.get_template_path(document_type)
            
            # Create docxtpl template
            doc = DocxTemplate(template_path)
            
            # Render the template with the context
            doc.render(context)
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{document_type.value}_{timestamp}.docx"
            output_path = OUTPUT_DIR / output_filename
            
            # Save the document
            doc.save(output_path)
            
            logger.info(f"Document generated successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to generate document: {str(e)}")
            raise ValueError(f"Document generation failed: {str(e)}")
    
    def generate_safe_document(self, safe_details: Dict[str, Any]) -> str:
        """
        Generate a SAFE document.
        
        Args:
            safe_details: Dictionary containing SAFE details
            
        Returns:
            Path to the generated document
        """
        return self.generate_document(DocumentType.SERIES_SEED_SAFE, safe_details)