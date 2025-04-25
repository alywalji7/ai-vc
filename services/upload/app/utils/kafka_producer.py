"""
Kafka Producer Utility for Upload Service.
Publishes file upload events to Kafka.
"""
import os
import json
import logging
from confluent_kafka import Producer

logger = logging.getLogger(__name__)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_FILE_UPLOADED = "file_uploaded"

def kafka_delivery_callback(err, msg):
    """Callback for Kafka message delivery reports."""
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

class KafkaProducer:
    """Kafka producer for publishing file upload events."""
    
    def __init__(self):
        """Initialize Kafka producer."""
        self.producer_config = {
            'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
            'client.id': 'upload-service',
        }
        self.producer = Producer(self.producer_config)
    
    def publish_file_uploaded_event(self, lp_id, file_s3_key):
        """
        Publish a file uploaded event to Kafka.
        
        Args:
            lp_id: ID of the LP uploading the file
            file_s3_key: S3 key of the uploaded file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            message = {
                "lp_id": lp_id,
                "file_s3_key": file_s3_key
            }
            
            # Serialize message to JSON
            message_json = json.dumps(message)
            
            # Produce message to Kafka topic
            self.producer.produce(
                KAFKA_TOPIC_FILE_UPLOADED,
                key=lp_id,
                value=message_json,
                callback=kafka_delivery_callback
            )
            
            # Flush producer to ensure message is sent
            self.producer.flush()
            
            logger.info(f"Published file_uploaded event for LP {lp_id}, file {file_s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing file_uploaded event: {str(e)}")
            return False

# Singleton instance of Kafka producer
kafka_producer = KafkaProducer()