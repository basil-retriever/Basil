from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
import os

load_dotenv()

from basil_search.routers import ask, site_scanner

app = FastAPI(title="BasilApi", version="1.0")

# CORS Configuration
def get_allowed_origins():
    """Parse ALLOWED_ORIGINS from environment variable"""
    origins_env = os.getenv("ALLOWED_ORIGINS", "*")
    
    if origins_env == "*":
        return ["*"]
    else:
        # Split by comma and strip whitespace
        return [origin.strip() for origin in origins_env.split(",") if origin.strip()]

allowed_origins = get_allowed_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
