"""
Base Agent class for Value-Add Agents.

This module provides a base class for all Value-Add agents, handling
Kafka subscription, message processing, and email sending.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List

from aiokafka import AIOKafkaConsumer
from config import KAFKA_BOOTSTRAP_SERVERS, EMAIL_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseAgent:
    """
    Base class for Value-Add agents that consume Kafka messages.
    
    This class provides common functionality for connecting to Kafka,
    consuming messages, and sending emails.
    """
    
    def __init__(
        self,
        topic: str,
        group_id: str,
        name: str,
        description: str
    ):
        """
        Initialize the base agent.
        
        Args:
            topic: Kafka topic to subscribe to
            group_id: Consumer group ID for Kafka
            name: Name of the agent
            description: Description of the agent
        """
        self.topic = topic
        self.group_id = group_id
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agent.{name.lower()}")
        self.consumer = None
        
        # Initialize consumer
        self._init_consumer()
        
        self.logger.info(f"Initialized {self.name} agent")
        
    def _init_consumer(self):
        """Initialize the Kafka consumer."""
        try:
            # In simulation mode, we don't need an actual Kafka connection
            if 'simulate.py' in sys.argv[0]:
                self.logger.info("Running in simulation mode - no Kafka connection needed")
                self.consumer = None
            else:
                self.logger.info(f"Creating Kafka consumer for topic {self.topic}")
                self.consumer = AIOKafkaConsumer(
                    self.topic,
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    group_id=self.group_id,
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    auto_offset_reset='earliest'
                )
        except Exception as e:
            self.logger.error(f"Error initializing Kafka consumer: {str(e)}")
            
    async def start(self):
        """Start consuming messages from Kafka."""
        if not self.consumer:
            self.logger.warning("No Kafka consumer available - not starting")
            return
            
        try:
            await self.consumer.start()
            self.logger.info(f"Started consuming from {self.topic}")
            
            async for msg in self.consumer:
                self.logger.info(f"Received message: {msg.key}")
                try:
                    await self.process_message(msg.value)
                    await self.consumer.commit()
                except Exception as e:
                    self.logger.error(f"Error processing message: {str(e)}")
                
        except Exception as e:
            self.logger.error(f"Error in Kafka consumer: {str(e)}")
        finally:
            try:
                await self.consumer.stop()
            except Exception as e:
                self.logger.error(f"Error stopping consumer: {str(e)}")
                
    async def process_message(self, message: Dict[str, Any]) -> bool:
        """
        Process a message from Kafka.
        
        This method should be overridden by subclasses.
        
        Args:
            message: The message payload
            
        Returns:
            True if processing was successful, False otherwise
        """
        self.logger.warning("Base process_message called - this should be overridden")
        return False
    
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email.
        
        In a real implementation, this would use SendGrid or another email service.
        For this exercise, we'll just log the email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            cc: Optional list of CC recipients
            
        Returns:
            True if the email was sent successfully, False otherwise
        """
        # Check if we have a SendGrid API key
        sendgrid_key = os.environ.get('SENDGRID_API_KEY')
        
        if sendgrid_key and sendgrid_key != 'mock_key':
            # In a real implementation, this would send using SendGrid
            try:
                from sendgrid import SendGridAPIClient
                from sendgrid.helpers.mail import Mail
                
                message = Mail(
                    from_email=EMAIL_CONFIG['default_from'],
                    to_emails=to,
                    subject=f"{EMAIL_CONFIG['subject_prefix']}{subject}",
                    html_content=body
                )
                
                if cc:
                    message.cc = cc
                    
                sg = SendGridAPIClient(sendgrid_key)
                response = sg.send(message)
                
                self.logger.info(f"Email sent via SendGrid: {response.status_code}")
                return response.status_code < 300
                
            except Exception as e:
                self.logger.error(f"Error sending email via SendGrid: {str(e)}")
                return False
        else:
            # Log the email for simulation purposes
            self.logger.info("SendGrid API key not found, logging email instead")
            self.logger.info(f"EMAIL TO: {to}")
            if cc:
                self.logger.info(f"EMAIL CC: {', '.join(cc)}")
            self.logger.info(f"EMAIL SUBJECT: {EMAIL_CONFIG['subject_prefix']}{subject}")
            self.logger.info(f"EMAIL BODY:\n{body}")
            return True