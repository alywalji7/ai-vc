"""
Negotiation analysis functionality for the Term Sheet Generator & Negotiator Bot.

This module provides functions for analyzing negotiation counter-offers,
determining deviation from original terms, and flagging terms that exceed
acceptable thresholds for escalation.
"""

import logging
import statistics
from typing import Dict, List, Any, Tuple

from ..models.schemas import CounterOffer, NegotiationAnalysis

logger = logging.getLogger(__name__)

# Define the standard deviation threshold for escalation
# Counter-offers deviating more than 2σ will be escalated
DEVIATION_THRESHOLD = 2.0


class NegotiationAnalyzer:
    """
    Analyzer for term sheet negotiation counter-offers.
    """
    
    def __init__(self, historical_data: List[Dict[str, Any]] = None):
        """
        Initialize the negotiation analyzer.
        
        Args:
            historical_data: Optional list of historical negotiation data
                for establishing baseline statistics
        """
        self.historical_data = historical_data or []
        
        # Calculate baseline statistics from historical data
        self.term_baselines = self._calculate_term_baselines()
        
    def _calculate_term_baselines(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate baseline statistics for different terms based on historical data.
        
        Returns:
            Dictionary mapping terms to their statistical baselines
        """
        if not self.historical_data:
            return {}
            
        # Group data by term
        term_data = {}
        for item in self.historical_data:
            term = item.get('term')
            deviation = item.get('deviation_percentage', 0)
            
            if term not in term_data:
                term_data[term] = []
                
            term_data[term].append(deviation)
            
        # Calculate statistics for each term
        baselines = {}
        for term, deviations in term_data.items():
            if len(deviations) >= 2:  # Need at least 2 points for standard deviation
                mean = statistics.mean(deviations)
                stdev = statistics.stdev(deviations)
            else:
                mean = deviations[0] if deviations else 0
                stdev = 10.0  # Default standard deviation if insufficient data
                
            baselines[term] = {
                'mean': mean,
                'stdev': stdev
            }
            
        return baselines
    
    def _calculate_deviation(self, original: float, proposed: float) -> float:
        """
        Calculate the percentage deviation between original and proposed values.
        
        Args:
            original: Original value
            proposed: Proposed value
            
        Returns:
            Percentage deviation (positive for increases, negative for decreases)
        """
        if original == 0:
            return float('inf') if proposed > 0 else float('-inf')
            
        return ((proposed - original) / original) * 100
    
    def analyze_counter_offer(
        self, 
        term: str, 
        original_value: Any, 
        proposed_value: Any
    ) -> Tuple[float, bool]:
        """
        Analyze a single counter-offer term to determine if it exceeds thresholds.
        
        Args:
            term: The term being negotiated
            original_value: Original value of the term
            proposed_value: Proposed new value of the term
            
        Returns:
            Tuple of (deviation percentage, requires escalation flag)
        """
        # For numeric terms, calculate percentage deviation
        if isinstance(original_value, (int, float)) and isinstance(proposed_value, (int, float)):
            deviation = self._calculate_deviation(original_value, proposed_value)
            
            # Get the baseline statistics for this term if available
            baseline = self.term_baselines.get(term, {'mean': 0, 'stdev': 10.0})
            stdev = baseline['stdev']
            
            # Check if the deviation exceeds the threshold
            normalized_deviation = abs(deviation) / stdev if stdev > 0 else float('inf')
            requires_escalation = normalized_deviation > DEVIATION_THRESHOLD
            
            return deviation, requires_escalation
            
        # For non-numeric terms, consider any change as significant
        # but don't escalate unless it's a critical term
        return 100.0 if original_value != proposed_value else 0.0, False
    
    def analyze_negotiation(
        self, 
        original_terms: Dict[str, Any], 
        proposed_terms: Dict[str, Any]
    ) -> NegotiationAnalysis:
        """
        Analyze all terms in a negotiation to identify deviations and escalation needs.
        
        Args:
            original_terms: Dictionary of original term values
            proposed_terms: Dictionary of proposed term values
            
        Returns:
            NegotiationAnalysis with counter-offers and escalation recommendations
        """
        counter_offers = []
        requires_escalation = False
        escalation_reason = None
        
        # Critical terms that should trigger escalation if they change significantly
        critical_terms = {'valuation_cap', 'discount_rate', 'investment_amount'}
        
        # Analyze each term in the proposed terms
        for term, proposed_value in proposed_terms.items():
            if term in original_terms:
                original_value = original_terms[term]
                
                # Skip if values are identical
                if original_value == proposed_value:
                    continue
                    
                # Analyze this counter-offer
                deviation, term_requires_escalation = self.analyze_counter_offer(
                    term, original_value, proposed_value
                )
                
                # Force escalation for critical terms
                if term in critical_terms and abs(deviation) > 15:  # 15% change in critical terms
                    term_requires_escalation = True
                
                # Create counter offer object
                counter_offer = CounterOffer(
                    term=term,
                    original_value=original_value,
                    proposed_value=proposed_value,
                    deviation_percentage=deviation,
                    is_extreme=term_requires_escalation
                )
                
                counter_offers.append(counter_offer)
                
                # Update escalation status
                if term_requires_escalation:
                    requires_escalation = True
                    if not escalation_reason:
                        escalation_reason = f"Term '{term}' deviation of {deviation:.2f}% exceeds threshold"
        
        return NegotiationAnalysis(
            counter_offers=counter_offers,
            requires_escalation=requires_escalation,
            escalation_reason=escalation_reason
        )