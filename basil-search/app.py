from fastapi import FastAPI
from dotenv import load_dotenv
import uvicorn
import os

load_dotenv()

from routers import ask, detect_intent, site_scanner

app = FastAPI(title="BasilApi", version="1.0")

app.include_router(detect_intent.router)
app.include_router(ask.router)
app.include_router(site_scanner.router)

def main():
    """Entry point for basil command"""
    print("🌿 Basil - AI-Powered Website Search Engine")
    print("Use 'basil-server' to start the server or 'basil-pipeline' to process websites")

def run_server():
    """Entry point for basil-server command"""
    uvicorn.run(
        "app:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("RELOAD", "false").lower() == "true"
    )

if __name__ == "__main__":
    run_server()
