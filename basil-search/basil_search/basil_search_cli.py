#!/usr/bin/env python3
"""
Basil CLI entry points for console scripts
"""
import os
import sys
from pathlib import Path

def run_server():
    """Entry point for basil-server command"""
    # Change to current working directory to find .env and data files
    cwd = os.getcwd()
    
    # Add the basil-search directory to Python path for imports
    basil_search_path = Path(__file__).parent
    sys.path.insert(0, str(basil_search_path))
    
    # Change to CWD so .env and data directories are found
    original_cwd = os.getcwd()
    
    try:
        from dotenv import load_dotenv
        import uvicorn
        
        # Load .env from current working directory
        env_path = Path(cwd) / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        else:
            load_dotenv()  # Try default locations
        
        # Import app after setting up paths  
        from basil_search.app import app as fastapi_app
        
        uvicorn.run(
            fastapi_app,
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", 8000)),
            reload=os.getenv("RELOAD", "false").lower() == "true"
        )
    finally:
        os.chdir(original_cwd)

def run_pipeline():
    """Entry point for basil-pipeline command"""
    # Change to current working directory to find .env and data files
    cwd = os.getcwd()
    
    # Add the basil-search directory to Python path for imports
    basil_search_path = Path(__file__).parent
    sys.path.insert(0, str(basil_search_path))
    
    # Change to CWD so .env and data directories are found
    original_cwd = os.getcwd()
    
    try:
        from basil_search.pipeline import main
        main()
    finally:
        os.chdir(original_cwd)

if __name__ == "__main__":
    print("🌿 Basil - AI-Powered Website Search Engine")
    print("Use 'basil-server' to start the server or 'basil-pipeline' to process websites")