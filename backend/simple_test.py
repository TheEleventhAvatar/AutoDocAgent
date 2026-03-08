from fastapi import FastAPI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="AutoDoc Agent Test")

@app.get("/")
async def root():
    return {"message": "AutoDoc Agent Backend is running!"}

@app.get("/health")
async def health_check():
    api_key = os.getenv("OPENAI_API_KEY")
    return {
        "status": "healthy",
        "api_key_configured": bool(api_key and api_key.startswith("sk-proj-"))
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting server on http://localhost:8000")
    uvicorn.run("simple_test:app", host="0.0.0.0", port=8000, reload=True)
