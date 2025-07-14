from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import subprocess
import os
import logging
from pathlib import Path

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("/index")
async def index_site(site: str, background_tasks: BackgroundTasks):
    """
    Index a website by running the pipeline.py script with the provided site URL.
    
    Args:
        site: The URL of the site to index
        
    Returns:
        JSON response indicating the indexing has started
    """
    if not site:
        raise HTTPException(status_code=400, detail="Site parameter is required")
    
    # Validate URL format (basic validation)
    if not (site.startswith('http://') or site.startswith('https://')):
        raise HTTPException(status_code=400, detail="Site must be a valid URL starting with http:// or https://")
    
    # Add the indexing task to background tasks
    background_tasks.add_task(run_pipeline, site)
    
    return JSONResponse(
        status_code=202,
        content={
            "message": f"Site indexing started for {site}",
            "status": "accepted",
            "site": site
        }
    )

def run_pipeline(site_url: str):
    """
    Run the pipeline.py script as a subprocess.
    
    Args:
        site_url: The URL to index
    """
    try:
        # Get the directory where pipeline.py is located
        pipeline_dir = Path(__file__).parent.parent
        pipeline_script = pipeline_dir / "pipeline.py"
        
        # Construct the command
        cmd = [
            "python3", 
            str(pipeline_script), 
            "--url", 
            site_url, 
            "--all"
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        # Run the command
        result = subprocess.run(
            cmd,
            cwd=str(pipeline_dir),
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes timeout
        )
        
        if result.returncode == 0:
            logger.info(f"Pipeline completed successfully for {site_url}")
            logger.info(f"Output: {result.stdout}")
        else:
            logger.error(f"Pipeline failed for {site_url}")
            logger.error(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logger.error(f"Pipeline timed out for {site_url}")
    except Exception as e:
        logger.error(f"Error running pipeline for {site_url}: {str(e)}")