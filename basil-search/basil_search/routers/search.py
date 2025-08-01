from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time
import logging
from basil_search.src.database import ChromaManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5

class SearchResult(BaseModel):
    document: str
    metadata: Dict[str, Any]
    similarity: float
    distance: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    processing_time: Optional[float] = None

# Initialize ChromaDB manager
try:
    chroma_manager = ChromaManager()
except Exception as e:
    logger.error(f"Failed to initialize ChromaDB: {e}")
    chroma_manager = None

@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    if not chroma_manager:
        raise HTTPException(status_code=500, detail="Database not available. Please check ChromaDB setup.")
    
    try:
        start_time = time.time()
        
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        results = chroma_manager.search(
            query=request.query,
            n_results=request.max_results
        )
        
        search_results = [
            SearchResult(
                document=result['document'],
                metadata=result['metadata'],
                similarity=result['similarity'],
                distance=result['distance']
            )
            for result in results['results']
        ]
        
        processing_time = time.time() - start_time
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results),
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/search/query")
async def search_query(
    q: str = Query(..., description="Search query"),
    max_results: int = Query(5, ge=1, le=20, description="Maximum number of results")
):
    request = SearchRequest(query=q, max_results=max_results)
    return await search(request)

@router.get("/health")
async def health_check():
    if not chroma_manager:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": "ChromaDB not initialized"
        }
    
    try:
        stats = chroma_manager.get_collection_stats()
        return {
            "status": "healthy",
            "database": "connected",
            "collection_stats": stats
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.get("/stats")
async def get_stats():
    if not chroma_manager:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        stats = chroma_manager.get_collection_stats()
        return stats
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")