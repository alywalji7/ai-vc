import uvicorn
import os
from dotenv import load_dotenv
from app.api import create_app
from app.db import init_db

# Load environment variables from .env file if it exists
load_dotenv()

# Initialize the database
init_db()

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    # Get host and port from environment or use defaults
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8080"))
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )