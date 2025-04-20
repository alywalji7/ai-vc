"""
Negotiation Manager for the Term Sheet Generator & Negotiator Bot.

This module provides the core functionality for managing term sheet negotiations,
analyzing counter-offers, and escalating when necessary.
"""

import os
import uuid
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..models.schemas import (
    NegotiationMessage, 
    NegotiationSession,
    DocumentType,
    NegotiationAnalysis
)
from .gpt_client import GPTClient
from .negotiation_analyzer import NegotiationAnalyzer
from ..utils.slack import send_escalation_notification

logger = logging.getLogger(__name__)

# Directory to store negotiation sessions
SESSIONS_DIR = "data/negotiation_sessions"


class NegotiationManager:
    """
    Manager for term sheet negotiations.
    """
    
    def __init__(self):
        """Initialize the negotiation manager."""
        # Create sessions directory if it doesn't exist
        os.makedirs(SESSIONS_DIR, exist_ok=True)
        
        # Initialize components
        self.gpt_client = GPTClient()
        self.analyzer = NegotiationAnalyzer()
        
        # In-memory cache of active sessions
        self.active_sessions = {}
        
    def create_session(
        self, 
        document_type: DocumentType,
        company_id: str,
        investor_id: str,
        original_terms: Dict[str, Any]
    ) -> NegotiationSession:
        """
        Create a new negotiation session.
        
        Args:
            document_type: Type of document being negotiated
            company_id: ID of the company
            investor_id: ID of the investor
            original_terms: Original terms of the term sheet
            
        Returns:
            New negotiation session
        """
        session_id = str(uuid.uuid4())
        
        # Create session
        session = NegotiationSession(
            session_id=session_id,
            document_type=document_type,
            company_id=company_id,
            investor_id=investor_id,
            original_terms=original_terms,
            current_terms=original_terms.copy(),
            messages=[],
            status="active"
        )
        
        # Save session to disk
        self._save_session(session)
        
        # Add to active sessions cache
        self.active_sessions[session_id] = session
        
        return session
        
    def get_session(self, session_id: str) -> Optional[NegotiationSession]:
        """
        Get a negotiation session by ID.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            Negotiation session or None if not found
        """
        # Check active sessions first
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
            
        # Otherwise load from disk
        try:
            session_path = os.path.join(SESSIONS_DIR, f"{session_id}.json")
            if not os.path.exists(session_path):
                return None
                
            with open(session_path, 'r') as f:
                session_data = json.load(f)
                
            return NegotiationSession(**session_data)
            
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {str(e)}")
            return None
            
    def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str
    ) -> Optional[NegotiationSession]:
        """
        Add a message to a negotiation session.
        
        Args:
            session_id: ID of the session
            role: Role of the sender (user/assistant/system)
            content: Message content
            
        Returns:
            Updated session or None if session not found
        """
        session = self.get_session(session_id)
        if not session:
            return None
            
        # Create message
        message = NegotiationMessage(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat()
        )
        
        # Add message to session
        session.messages.append(message)
        
        # Save updated session
        self._save_session(session)
        
        return session
        
    def generate_response(
        self, 
        session_id: str
    ) -> Optional[NegotiationSession]:
        """
        Generate a response to the latest message in a negotiation session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Updated session or None if session not found
        """
        session = self.get_session(session_id)
        if not session or session.status != "active" or not session.messages:
            return None
            
        # If the last message was from the assistant, don't respond
        if session.messages[-1].role == "assistant":
            return session
            
        try:
            # Generate response using GPT
            response = self.gpt_client.generate_response(
                session.messages, 
                session.original_terms
            )
            
            # Add response to session
            self.add_message(session_id, "assistant", response)
            
            # Get updated session
            session = self.get_session(session_id)
            
            # Check if this was a counter-offer
            if len(session.messages) >= 2 and session.messages[-2].role == "user":
                self._process_counter_offer(session)
                
            return session
            
        except Exception as e:
            logger.error(f"Error generating response for session {session_id}: {str(e)}")
            return None
            
    def _process_counter_offer(self, session: NegotiationSession) -> None:
        """
        Process a potential counter-offer from the user.
        
        Args:
            session: The negotiation session
        """
        try:
            # Extract counter-offer terms using GPT
            counter_offer_terms = self.gpt_client.analyze_counter_offer(
                session.messages,
                session.original_terms
            )
            
            # If no counter-offer terms were extracted, do nothing
            if not counter_offer_terms:
                return
                
            # Analyze the counter-offer for deviations and escalation needs
            analysis = self.analyzer.analyze_negotiation(
                session.original_terms,
                {**session.original_terms, **counter_offer_terms}
            )
            
            # Update current terms
            for term, value in counter_offer_terms.items():
                if term in session.current_terms:
                    session.current_terms[term] = value
            
            # If escalation is required, handle it
            if analysis.requires_escalation:
                self._handle_escalation(session, analysis)
                
            # Save updated session
            self._save_session(session)
            
        except Exception as e:
            logger.error(f"Error processing counter offer: {str(e)}")
            
    def _handle_escalation(
        self, 
        session: NegotiationSession, 
        analysis: NegotiationAnalysis
    ) -> None:
        """
        Handle a negotiation escalation.
        
        Args:
            session: The negotiation session
            analysis: Analysis results
        """
        # Update session status
        session.status = "escalated"
        
        # Add system message about escalation
        escalation_message = (
            f"This negotiation has been escalated for human review due to: "
            f"{analysis.escalation_reason}"
        )
        
        self.add_message(session.session_id, "system", escalation_message)
        
        # Find the most extreme counter-offer
        most_extreme = None
        largest_deviation = 0
        
        for offer in analysis.counter_offers:
            if offer.is_extreme and abs(offer.deviation_percentage) > largest_deviation:
                most_extreme = offer
                largest_deviation = abs(offer.deviation_percentage)
                
        # If we found an extreme counter-offer, send notification
        if most_extreme:
            company_name = f"Company {session.company_id}"  # Placeholder, ideally get real name
            investor_name = f"Investor {session.investor_id}"  # Placeholder, ideally get real name
            
            send_escalation_notification(
                most_extreme.dict(),
                session.session_id,
                company_name,
                investor_name
            )
            
    def _save_session(self, session: NegotiationSession) -> None:
        """
        Save a negotiation session to disk.
        
        Args:
            session: The session to save
        """
        try:
            # Convert session to dictionary
            session_data = session.dict()
            
            # Save to file
            session_path = os.path.join(SESSIONS_DIR, f"{session.session_id}.json")
            with open(session_path, 'w') as f:
                json.dump(session_data, f, indent=2)
                
            # Update in-memory cache
            self.active_sessions[session.session_id] = session
            
        except Exception as e:
            logger.error(f"Error saving session {session.session_id}: {str(e)}")