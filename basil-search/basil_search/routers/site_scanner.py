from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import subprocess
import os
import logging
from pathlib import Path
import re
from urllib.parse import urlparse

router = APIRouter()

logger = logging.getLogger(__name__)

class InternalSiteRequest(BaseModel):
    site: str
    max_pages: Optional[int] = 50
    auth_header: Optional[str] = None
    auth_token: Optional[str] = None
    custom_headers: Optional[dict] = None

def is_internal_url(url: str) -> bool:
    """Check if URL is internal/localhost/private network"""
    parsed = urlparse(url)
    hostname = parsed.hostname
    
    if not hostname:
        return False
    
    # Check for localhost variations
    localhost_patterns = [
        'localhost', '127.0.0.1', '0.0.0.0', '::1'
    ]
    
    # Check for private IP ranges
    private_ip_patterns = [
        r'^10\.',  # 10.0.0.0/8
        r'^192\.168\.',  # 192.168.0.0/16
        r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',  # 172.16.0.0/12
        r'^169\.254\.',  # Link-local
    ]
    
    # Check localhost
    if hostname.lower() in localhost_patterns:
        return True
    
    # Check private IPs
    for pattern in private_ip_patterns:
        if re.match(pattern, hostname):
            return True
    
    # Check for .local domains (common in development)
    if hostname.endswith('.local'):
        return True
    
    return False

def validate_internal_url(url: str) -> bool:
    """Validate internal URL format"""
    if not (url.startswith('http://') or url.startswith('https://')):
        return False
    
    parsed = urlparse(url)
    if not parsed.hostname:
        return False
    
    return is_internal_url(url)

@router.post("/index-internal")
async def index_internal_site(request: InternalSiteRequest, background_tasks: BackgroundTasks):
    """
    Index an internal website or localhost application.
    
    Designed for:
    - localhost development servers (localhost:4200, localhost:3000, etc.)
    - Internal company sites (internal.company.com)
    - Private network services (192.168.1.100:8080)
    - Local documentation sites
    
    Args:
        request: InternalSiteRequest with site URL and optional auth
        
    Returns:
        JSON response indicating the indexing has started
    """
    site = request.site.strip()
    
    if not site:
        raise HTTPException(status_code=400, detail="Site parameter is required")
    
    # Validate internal URL
    if not validate_internal_url(site):
        raise HTTPException(
            status_code=400, 
            detail="Site must be an internal URL (localhost, private IP, or .local domain)"
        )
    
    # Add the indexing task to background tasks
    background_tasks.add_task(run_internal_pipeline, request)
    
    return JSONResponse(
        status_code=202,
        content={
            "message": f"Internal site indexing started for {site}",
            "status": "accepted",
            "site": site,
            "max_pages": request.max_pages,
            "type": "internal"
        }
    )

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

def run_internal_pipeline(request: InternalSiteRequest):
    """
    Run the pipeline.py script for internal sites with enhanced configuration.
    
    Args:
        request: InternalSiteRequest containing site URL and auth details
    """
    try:
        # Get the directory where pipeline.py is located
        pipeline_dir = Path(__file__).parent.parent
        pipeline_script = pipeline_dir / "pipeline.py"
        
        # Construct the command with internal site parameters
        cmd = [
            "python3", 
            str(pipeline_script), 
            "--url", 
            request.site, 
            "--max-pages",
            str(request.max_pages),
            "--internal",  # Flag to indicate internal processing
            "--all"
        ]
        
        # Set environment variables for authentication if provided
        env = os.environ.copy()
        if request.auth_header:
            env['BASIL_AUTH_HEADER'] = request.auth_header
        if request.auth_token:
            env['BASIL_AUTH_TOKEN'] = request.auth_token
        if request.custom_headers:
            import json
            env['BASIL_CUSTOM_HEADERS'] = json.dumps(request.custom_headers)
        
        logger.info(f"Running internal pipeline command: {' '.join(cmd)}")
        
        # Run the command with extended timeout for internal sites
        result = subprocess.run(
            cmd,
            cwd=str(pipeline_dir),
            capture_output=True,
            text=True,
            timeout=3600,  # 60 minutes timeout for internal sites
            env=env
        )
        
        if result.returncode == 0:
            logger.info(f"Internal pipeline completed successfully for {request.site}")
            logger.info(f"Output: {result.stdout}")
        else:
            logger.error(f"Internal pipeline failed for {request.site}")
            logger.error(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logger.error(f"Internal pipeline timed out for {request.site}")
    except Exception as e:
        logger.error(f"Error running internal pipeline for {request.site}: {str(e)}")