"""
Tests for the negotiation analyzer module.
"""

import pytest
from app.core.negotiation_analyzer import NegotiationAnalyzer


@pytest.fixture
def analyzer():
    """Fixture for the negotiation analyzer."""
    return NegotiationAnalyzer()


@pytest.fixture
def original_terms():
    """Fixture for original terms."""
    return {
        "investment_amount": 500000,
        "valuation_cap": 8000000,
        "discount_rate": 20
    }


def test_normal_counter_offer(analyzer, original_terms):
    """Test analyzing a normal counter-offer (within acceptable range)."""
    # Counter-offer within normal range (5% increase in valuation cap)
    counter_offer_terms = {
        "investment_amount": 500000,
        "valuation_cap": 8400000,  # 5% increase
        "discount_rate": 20
    }
    
    # Analyze negotiation
    analysis = analyzer.analyze_negotiation(original_terms, counter_offer_terms)
    
    # Verify analysis
    assert len(analysis.counter_offers) == 1
    assert analysis.counter_offers[0].term == "valuation_cap"
    assert analysis.counter_offers[0].original_value == 8000000
    assert analysis.counter_offers[0].proposed_value == 8400000
    assert analysis.counter_offers[0].deviation_percentage == 5.0
    assert not analysis.counter_offers[0].is_extreme
    assert not analysis.requires_escalation
    assert analysis.escalation_reason is None


def test_extreme_counter_offer(analyzer, original_terms):
    """Test analyzing an extreme counter-offer (outside acceptable range)."""
    # Extreme counter-offer (100% increase in valuation cap)
    counter_offer_terms = {
        "investment_amount": 500000,
        "valuation_cap": 16000000,  # 100% increase
        "discount_rate": 15  # 25% decrease
    }
    
    # Analyze negotiation
    analysis = analyzer.analyze_negotiation(original_terms, counter_offer_terms)
    
    # Verify analysis
    assert len(analysis.counter_offers) == 2
    assert analysis.requires_escalation
    assert analysis.escalation_reason is not None
    
    # Find the extreme counter-offer (valuation cap)
    valuation_offer = next(
        (offer for offer in analysis.counter_offers if offer.term == "valuation_cap"),
        None
    )
    assert valuation_offer is not None
    assert valuation_offer.original_value == 8000000
    assert valuation_offer.proposed_value == 16000000
    assert valuation_offer.deviation_percentage == 100.0
    assert valuation_offer.is_extreme


def test_calculate_deviation(analyzer):
    """Test calculating deviation percentage."""
    # Test zero original value
    assert analyzer._calculate_deviation(0, 100) == float('inf')
    assert analyzer._calculate_deviation(0, -100) == float('-inf')
    
    # Test positive deviation
    assert analyzer._calculate_deviation(100, 200) == 100.0
    
    # Test negative deviation
    assert analyzer._calculate_deviation(100, 75) == -25.0
    
    # Test no deviation
    assert analyzer._calculate_deviation(100, 100) == 0.0


def test_with_historical_data():
    """Test analyzer with historical data."""
    # Create historical data
    historical_data = [
        {"term": "valuation_cap", "deviation_percentage": 10},
        {"term": "valuation_cap", "deviation_percentage": 15},
        {"term": "valuation_cap", "deviation_percentage": 20},
        {"term": "discount_rate", "deviation_percentage": -5},
        {"term": "discount_rate", "deviation_percentage": -8},
    ]
    
    # Create analyzer with historical data
    analyzer = NegotiationAnalyzer(historical_data)
    
    # Verify baselines were calculated
    assert "valuation_cap" in analyzer.term_baselines
    assert "discount_rate" in analyzer.term_baselines
    
    # Verify statistics
    assert abs(analyzer.term_baselines["valuation_cap"]["mean"] - 15) <= 0.1  # Mean should be around 15
    assert analyzer.term_baselines["valuation_cap"]["stdev"] > 0  # Should have a positive stdev