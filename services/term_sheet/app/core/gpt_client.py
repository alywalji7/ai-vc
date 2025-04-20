"""
OpenAI GPT integration for the Term Sheet Generator & Negotiator Bot.

This module provides functions for interacting with the OpenAI GPT-4o API
to generate responses in negotiation conversations.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional

from openai import OpenAI
from ..models.schemas import NegotiationMessage

logger = logging.getLogger(__name__)

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
GPT_MODEL = "gpt-4o"

# Get API key from environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


class GPTClient:
    """
    Client for interacting with OpenAI's GPT models.
    """
    
    def __init__(self, system_prompt: Optional[str] = None):
        """
        Initialize the GPT client.
        
        Args:
            system_prompt: Optional system prompt to set the behavior of the model
        """
        if not OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY environment variable not set")
            raise ValueError("OpenAI API key is required")
            
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        
    def _get_default_system_prompt(self) -> str:
        """
        Get the default system prompt for term sheet negotiations.
        
        Returns:
            Default system prompt string
        """
        return """
        You are an expert term sheet negotiator representing a venture capital firm. 
        Your role is to negotiate term sheets with startup founders professionally and fairly.
        
        Guidelines:
        - Maintain a professional and constructive tone throughout negotiations
        - Focus on creating win-win scenarios where possible
        - Be detailed and precise when discussing terms
        - Explain the reasoning behind your positions
        - Be firm but fair on terms important to investors (liquidation preferences, pro-rata rights)
        - Understand normal ranges for key terms at different funding stages
        
        Key term ranges:
        - SAFE valuation caps: $3M-$20M for pre-seed/seed
        - Discount rates: 10%-25%
        - Equity rounds valuations: Seed ($5M-$15M), Series A ($15M-$50M)
        - Liquidation preference: 1x non-participating is standard
        - Board seats: 1 for lead investor in Series A, observer rights in seed
        
        When providing counter-offers, include clear justification for your position.
        """
        
    def generate_response(
        self, 
        messages: List[NegotiationMessage], 
        original_terms: Dict[str, Any]
    ) -> str:
        """
        Generate a response in a negotiation conversation.
        
        Args:
            messages: Previous messages in the conversation
            original_terms: Original terms of the term sheet
            
        Returns:
            Generated response from the GPT model
        """
        try:
            # Format messages for OpenAI API
            formatted_messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add original terms context
            terms_context = "Original Term Sheet Terms:\n"
            for term, value in original_terms.items():
                terms_context += f"- {term}: {value}\n"
                
            formatted_messages.append({
                "role": "system", 
                "content": terms_context
            })
            
            # Add conversation history
            for msg in messages:
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=GPT_MODEL,
                messages=formatted_messages,
                temperature=0.7,
                max_tokens=1000,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating GPT response: {str(e)}")
            raise
            
    def analyze_counter_offer(
        self, 
        messages: List[NegotiationMessage], 
        original_terms: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract counter-offer terms from a negotiation message.
        
        Args:
            messages: Conversation history including the counter-offer
            original_terms: Original terms for comparison
            
        Returns:
            Dictionary of extracted counter-offer terms
        """
        try:
            # Format messages for OpenAI API
            formatted_messages = [
                {
                    "role": "system", 
                    "content": """
                    Extract the specific counter-offer terms from the negotiation messages.
                    Identify any changes from the original terms and return them as a JSON object.
                    
                    For example, if original valuation_cap was $10M and counter-offer is $12M,
                    include { "valuation_cap": 12000000 } in your response.
                    
                    Only include terms that are different from the original terms.
                    """
                }
            ]
            
            # Add original terms context
            terms_context = "Original Term Sheet Terms:\n"
            for term, value in original_terms.items():
                terms_context += f"- {term}: {value}\n"
                
            formatted_messages.append({
                "role": "system", 
                "content": terms_context
            })
            
            # Add conversation history
            for msg in messages:
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Add final instruction to ensure JSON output
            formatted_messages.append({
                "role": "user",
                "content": "Extract the counter-offer terms as JSON. Only include terms that differ from the original terms."
            })
            
            # Call the OpenAI API with JSON response format
            response = self.client.chat.completions.create(
                model=GPT_MODEL,
                messages=formatted_messages,
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=500,
            )
            
            # Parse the response
            response_text = response.choices[0].message.content
            counter_offer_terms = json.loads(response_text)
            
            return counter_offer_terms
            
        except Exception as e:
            logger.error(f"Error analyzing counter offer: {str(e)}")
            return {}