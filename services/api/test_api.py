import uvicorn

if __name__ == "__main__":
    print("Starting API server on port 8888")
    uvicorn.run("main:app", host="0.0.0.0", port=8888)