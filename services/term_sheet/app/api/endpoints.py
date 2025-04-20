"""
API endpoints for the Term Sheet Generator & Negotiator Bot.

This module defines FastAPI routes for generating term sheets
and handling term sheet negotiations.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks
from fastapi.responses import FileResponse

from ..models.schemas import TermSheetRequest, DocumentType, NegotiationMessage
from ..core.document_generator import DocumentGenerator
from ..core.negotiation_manager import NegotiationManager

logger = logging.getLogger(__name__)

router = APIRouter()
document_generator = DocumentGenerator()
negotiation_manager = NegotiationManager()

# Directory to create for data/session logs
import os
os.makedirs("data/negotiation_sessions", exist_ok=True)
os.makedirs("logs", exist_ok=True)


@router.post("/generate")
async def generate_term_sheet(request: TermSheetRequest) -> Dict[str, Any]:
    """
    Generate a term sheet document based on the provided request.
    
    Args:
        request: Term sheet generation request
        
    Returns:
        Dictionary with generated document path and document type
    """
    try:
        document_path = None
        
        # Handle different document types
        if request.document_type == DocumentType.SERIES_SEED_SAFE:
            if not request.safe_details:
                raise HTTPException(status_code=400, detail="SAFE details required for Series Seed SAFE document")
                
            # Generate SAFE document
            document_path = document_generator.generate_safe_document(request.safe_details.dict())
            
        else:
            # Add handlers for other document types here
            raise HTTPException(status_code=400, detail=f"Document type {request.document_type} not supported yet")
            
        return {
            "document_type": request.document_type,
            "document_path": document_path
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating term sheet: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate term sheet document")


@router.get("/download/{document_path:path}")
async def download_document(document_path: str) -> FileResponse:
    """
    Download a generated document.
    
    Args:
        document_path: Path to the document
        
    Returns:
        File download response
    """
    try:
        # Security check to ensure path is in the output directory
        if "../" in document_path or not os.path.exists(document_path):
            raise HTTPException(status_code=404, detail="Document not found")
            
        return FileResponse(
            document_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=os.path.basename(document_path)
        )
        
    except Exception as e:
        logger.error(f"Error downloading document: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download document")


@router.post("/negotiate/session")
async def create_negotiation_session(
    document_type: DocumentType,
    company_id: str,
    investor_id: str,
    original_terms: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a new negotiation session.
    
    Args:
        document_type: Type of document being negotiated
        company_id: ID of the company
        investor_id: ID of the investor
        original_terms: Original terms of the term sheet
        
    Returns:
        Dictionary with negotiation session details
    """
    try:
        session = negotiation_manager.create_session(
            document_type,
            company_id,
            investor_id,
            original_terms
        )
        
        return {"session_id": session.session_id}
        
    except Exception as e:
        logger.error(f"Error creating negotiation session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create negotiation session")


@router.get("/negotiate/session/{session_id}")
async def get_negotiation_session(session_id: str) -> Dict[str, Any]:
    """
    Get details of a negotiation session.
    
    Args:
        session_id: ID of the session
        
    Returns:
        Dictionary with negotiation session details
    """
    session = negotiation_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Negotiation session not found")
        
    return session.dict()


@router.websocket("/negotiate/chat/{session_id}")
async def negotiate_chat(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time term sheet negotiation chat.
    
    Args:
        websocket: WebSocket connection
        session_id: ID of the negotiation session
    """
    await websocket.accept()
    
    try:
        # Check if session exists
        session = negotiation_manager.get_session(session_id)
        if not session:
            await websocket.send_json({"error": "Negotiation session not found"})
            await websocket.close()
            return
            
        # Send session history
        await websocket.send_json({
            "type": "history",
            "messages": [msg.dict() for msg in session.messages]
        })
        
        # Main chat loop
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = {"content": data, "role": "user"}
            
            # Add message to session
            session = negotiation_manager.add_message(session_id, "user", data)
            if not session:
                await websocket.send_json({"error": "Failed to add message"})
                continue
                
            # Send acknowledgement
            await websocket.send_json({
                "type": "message_received",
                "message": message_data
            })
            
            # Generate AI response
            updated_session = negotiation_manager.generate_response(session_id)
            if not updated_session:
                await websocket.send_json({"error": "Failed to generate response"})
                continue
                
            # Send AI response
            last_message = updated_session.messages[-1]
            await websocket.send_json({
                "type": "message",
                "message": last_message.dict()
            })
            
            # Check if negotiation was escalated
            if updated_session.status == "escalated":
                await websocket.send_json({
                    "type": "escalation",
                    "message": "This negotiation has been escalated for human review due to unusual counter-offer terms."
                })
                
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from negotiation session {session_id}")
    except Exception as e:
        logger.error(f"Error in negotiation chat: {str(e)}")
        await websocket.close()