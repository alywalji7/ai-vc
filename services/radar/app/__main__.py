"""
Direct entry point for running the radar service.
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8095,
        reload=True, 
        log_level="info",
        app_dir="services/radar/app"
    )