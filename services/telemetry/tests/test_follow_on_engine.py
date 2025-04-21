"""
Test script for the Follow-On Engine functionality.

This script validates that the Follow-On Engine correctly identifies
companies that require follow-on investments based on preset criteria.
"""
import os
import sys
import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path to allow importing from the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import Base, PortfolioCompany, FinancialMetric, FollowOnDecision
from data.follow_on_engine import FollowOnEngine
from tests.data_generator import generate_test_data

class TestFollowOnEngine(unittest.TestCase):
    """
    Test case for the Follow-On Engine functionality.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        # Create an in-memory SQLite database for testing
        cls.engine = create_engine("sqlite:///:memory:")
        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        
        # Create all the tables
        Base.metadata.create_all(cls.engine)
    
    def setUp(self):
        """Set up the test database with sample data before each test."""
        self.db = self.SessionLocal()
        # Generate test data
        generate_test_data(self.db)
    
    def tearDown(self):
        """Clean up after each test."""
        self.db.close()
    
    def test_growth_trigger(self):
        """Test that the growth trigger works correctly."""
        # Run the follow-on engine
        follow_on_engine = FollowOnEngine(self.db)
        decisions = follow_on_engine.analyze_all_companies()
        
        # Find decisions for the high-growth company
        high_growth_decisions = [d for d in decisions if d["company_id"] == "highgrowth-saas-1"]
        
        # Assert that a growth-triggered decision was made
        self.assertTrue(any(d["trigger_type"] == "growth" for d in high_growth_decisions),
                        "No growth-triggered follow-on decision found for high-growth company")
        
        # Find the growth-triggered decision
        growth_decision = next((d for d in high_growth_decisions if d["trigger_type"] == "growth"), None)
        
        # Assert that it's a super-pro-rata decision
        self.assertTrue(growth_decision["super_pro_rata"],
                       "Growth-triggered decision should recommend super-pro-rata investment")
    
    def test_runway_trigger(self):
        """Test that the runway trigger works correctly."""
        # Run the follow-on engine
        follow_on_engine = FollowOnEngine(self.db)
        decisions = follow_on_engine.analyze_all_companies()
        
        # Find decisions for the low-runway company
        low_runway_decisions = [d for d in decisions if d["company_id"] == "lowrunway-hardware-1"]
        
        # Assert that a runway-triggered decision was made
        self.assertTrue(any(d["trigger_type"] == "runway" for d in low_runway_decisions),
                       "No runway-triggered follow-on decision found for low-runway company")
        
        # Get the runway-triggered decision
        runway_decision = next((d for d in low_runway_decisions if d["trigger_type"] == "runway"), None)
        
        # Assert that it recommends enough to extend the runway
        self.assertIsNotNone(runway_decision, "No runway-triggered decision found")
        self.assertGreater(runway_decision["recommended_amount"], 0,
                          "Runway-triggered decision should recommend a positive investment amount")
    
    def test_no_trigger_for_stable_company(self):
        """Test that no follow-on is triggered for stable companies."""
        # Run the follow-on engine
        follow_on_engine = FollowOnEngine(self.db)
        decisions = follow_on_engine.analyze_all_companies()
        
        # Check for decisions for the stable company
        stable_decisions = [d for d in decisions if d["company_id"] == "stable-fintech-1"]
        
        # Assert that no decisions were made for the stable company
        self.assertEqual(len(stable_decisions), 0,
                        "No follow-on decisions should be triggered for stable company")
    
    def test_direct_follow_on_decision(self):
        """Test the direct follow_on_decision function."""
        # Run a direct follow-on decision for the high-growth company
        follow_on_engine = FollowOnEngine(self.db)
        decision = follow_on_engine.follow_on_decision("highgrowth-saas-1")
        
        # Assert that a decision was returned
        self.assertIsNotNone(decision, 
                            "follow_on_decision should return a decision for high-growth company")
        self.assertEqual(decision["company_id"], "highgrowth-saas-1",
                        "Decision should be for the requested company")
        self.assertTrue(decision["super_pro_rata"],
                       "Decision for high-growth company should be super-pro-rata")

if __name__ == "__main__":
    unittest.main()