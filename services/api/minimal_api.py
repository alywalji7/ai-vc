from fastapi import FastAPI
import uvicorn
from datetime import datetime

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/")
def root():
    return {"message": "API is running"}

if __name__ == "__main__":
    print("Starting minimal API server on port 8050")
    uvicorn.run(app, host="0.0.0.0", port=8050)