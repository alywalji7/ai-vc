"""
Base agent class for value-add agents.
"""

import json
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from aiokafka import AIOKafkaConsumer

from config import KAFKA_BOOTSTRAP_SERVERS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseAgent(ABC):
    """Base class for all value-add agents."""

    def __init__(self, topic: str, group_id: str, name: str, description: str):
        """
        Initialize the base agent.
        
        Args:
            topic: Kafka topic to subscribe to
            group_id: Kafka consumer group ID
            name: Agent name
            description: Agent description
        """
        self.topic = topic
        self.group_id = group_id
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agent.{name.lower()}")
        self.consumer = None
        self.running = False
    
    async def start(self):
        """Start the agent."""
        self.logger.info(f"Starting {self.name} ({self.description})")
        self.running = True
        
        # Initialize Kafka consumer
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            enable_auto_commit=False,
        )
        
        await self.consumer.start()
        self.logger.info(f"{self.name} subscribed to topic: {self.topic}")
        
        try:
            await self.consume_messages()
        finally:
            await self.stop()
    
    async def consume_messages(self):
        """Consume messages from Kafka topic."""
        async for message in self.consumer:
            self.logger.info(f"Received message from {message.topic} [partition={message.partition}, offset={message.offset}]")
            
            try:
                # Process the message
                await self.process_message(message.value)
                
                # Commit the offset
                await self.consumer.commit()
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
    
    async def stop(self):
        """Stop the agent."""
        self.logger.info(f"Stopping {self.name}")
        self.running = False
        
        if self.consumer:
            await self.consumer.stop()
    
    @abstractmethod
    async def process_message(self, message: Dict[str, Any]):
        """
        Process a message from the Kafka topic.
        
        Args:
            message: The message to process
        """
        pass
    
    async def send_email(self, to: str, subject: str, body: str, cc: Optional[str] = None):
        """
        Send an email (stub implementation).
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            cc: CC email address (optional)
        """
        # In a real implementation, this would send an actual email
        # For now, we'll just print the email to the console
        
        self.logger.info(f"Sending email from {self.name}")
        print("\n" + "=" * 80)
        print(f"From: {self.name} <ai.vc@example.com>")
        print(f"To: {to}")
        if cc:
            print(f"CC: {cc}")
        print(f"Subject: {subject}")
        print("=" * 80)
        print(body)
        print("=" * 80 + "\n")
        
        return True
    
    @classmethod
    async def run(cls, topic: str, group_id: str, name: str, description: str):
        """
        Run the agent.
        
        Args:
            topic: Kafka topic to subscribe to
            group_id: Kafka consumer group ID
            name: Agent name
            description: Agent description
        """
        agent = cls(topic, group_id, name, description)
        await agent.start()