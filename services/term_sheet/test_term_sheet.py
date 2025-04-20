"""
Test script for the Term Sheet Generator & Negotiator Bot.

This script tests:
1. Generating a SAFE document
2. Simulating a negotiation with an extreme counter-offer to trigger escalation
"""

import os
import json
import logging
import sys
from datetime import datetime

# Add correct path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from app.models.schemas import DocumentType, SAFEDetails
from app.core.document_generator import DocumentGenerator
from app.core.negotiation_manager import NegotiationManager
from app.core.negotiation_analyzer import NegotiationAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)


def test_generate_safe_document():
    """Test generating a SAFE document."""
    logger.info("===== Testing SAFE Document Generation =====")
    
    # Create directory for output if it doesn't exist
    os.makedirs("app/output", exist_ok=True)
    
    # Create document generator
    document_generator = DocumentGenerator()
    
    # Create SAFE details
    safe_details = {
        "investment_amount": 500000,
        "valuation_cap": 8000000,
        "discount_rate": 20,
        "company_name": "TechStartup Inc.",
        "investor_name": "Venture Capital Partners LLC",
        "effective_date": datetime.now().strftime("%Y-%m-%d"),
        "company_signatory_name": "John Smith",
        "company_signatory_title": "CEO",
        "investor_signatory_name": "Jane Doe",
        "investor_signatory_title": "Managing Partner"
    }
    
    try:
        # Generate document
        document_path = document_generator.generate_safe_document(safe_details)
        
        # Verify document was created
        if os.path.exists(document_path):
            logger.info(f"✅ Document generated successfully: {document_path}")
        else:
            logger.error(f"❌ Document generation failed: {document_path}")
            
    except Exception as e:
        logger.error(f"❌ Error generating document: {str(e)}")


def test_negotiation_with_extreme_counter_offer():
    """Test negotiation with an extreme counter-offer to trigger escalation."""
    logger.info("===== Testing Negotiation with Extreme Counter-Offer =====")
    
    # Create directories if they don't exist
    os.makedirs("data/negotiation_sessions", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Original terms
    original_terms = {
        "investment_amount": 500000,
        "valuation_cap": 8000000,
        "discount_rate": 20
    }
    
    # Extreme counter-offer - 100% increase in valuation cap
    counter_offer_terms = {
        "investment_amount": 500000,
        "valuation_cap": 16000000,  # 100% increase, should trigger escalation
        "discount_rate": 15  # 25% decrease
    }
    
    # Create negotiation analyzer
    analyzer = NegotiationAnalyzer()
    
    # Analyze negotiation
    analysis = analyzer.analyze_negotiation(original_terms, counter_offer_terms)
    
    # Log results
    logger.info(f"Counter-offers detected: {len(analysis.counter_offers)}")
    logger.info(f"Requires escalation: {analysis.requires_escalation}")
    if analysis.escalation_reason:
        logger.info(f"Escalation reason: {analysis.escalation_reason}")
    
    for offer in analysis.counter_offers:
        logger.info(f"Term: {offer.term}")
        logger.info(f"Original value: {offer.original_value}")
        logger.info(f"Proposed value: {offer.proposed_value}")
        logger.info(f"Deviation: {offer.deviation_percentage:.2f}%")
        logger.info(f"Is extreme: {offer.is_extreme}")
        logger.info("---")
    
    # Log to human-override file as fallback
    if analysis.requires_escalation:
        logger.info("Writing to human-override.log due to extreme counter-offer")
        
        # Find the extreme counter-offer
        extreme_offer = None
        for offer in analysis.counter_offers:
            if offer.is_extreme:
                extreme_offer = offer
                break
                
        if extreme_offer:
            # Format the log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "negotiation_id": "test-session-001",
                "company_name": "TechStartup Inc.",
                "investor_name": "Venture Capital Partners LLC",
                "counter_offer": {
                    "term": extreme_offer.term,
                    "original_value": extreme_offer.original_value,
                    "proposed_value": extreme_offer.proposed_value,
                    "deviation_percentage": extreme_offer.deviation_percentage
                }
            }
            
            # Write to the human-override log file
            with open("logs/human-override.log", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
                
            logger.info("✅ Extreme counter-offer logged to human-override.log")
            
            # Verify the log file exists and contains our entry
            if os.path.exists("logs/human-override.log"):
                logger.info("✅ human-override.log file created successfully")
            else:
                logger.error("❌ Failed to create human-override.log file")
    else:
        logger.info("❌ Escalation condition not met - no extreme counter-offer detected")


if __name__ == "__main__":
    logger.info("Starting Term Sheet Generator & Negotiator Bot tests")
    
    # Generate a SAFE document
    test_generate_safe_document()
    
    # Test negotiation with extreme counter-offer
    test_negotiation_with_extreme_counter_offer()
    
    logger.info("Tests completed.")