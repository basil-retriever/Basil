from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from basil_search.src.database import ChromaManager
from basil_search.src.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Website Search API",
    description="Semantic search API for website content",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chroma_manager = ChromaManager()

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

@app.get("/")
async def root():
    return {
        "message": "Website Search API",
        "version": "1.0.0",
        "endpoints": {
            "/search": "POST - Semantic search",
            "/search/query": "GET - Search with query parameter",
            "/health": "GET - Health check",
            "/stats": "GET - Collection statistics"
        }
    }

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    try:
        import time
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

@app.get("/search/query")
async def search_query(
    q: str = Query(..., description="Search query"),
    max_results: int = Query(5, ge=1, le=20, description="Maximum number of results")
):
    request = SearchRequest(query=q, max_results=max_results)
    return await search(request)

@app.get("/health")
async def health_check():
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

@app.get("/stats")
async def get_stats():
    try:
        stats = chroma_manager.get_collection_stats()
        return stats
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.post("/reload")
async def reload_database():
    try:
        chroma_manager.clear_collection()
        
        results = chroma_manager.load_processed_files()
        
        return {
            "message": "Database reloaded successfully",
            "loaded_documents": results
        }
        
    except Exception as e:
        logger.error(f"Reload error: {e}")
        raise HTTPException(status_code=500, detail=f"Reload failed: {str(e)}")

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "message": "Please check the API documentation"}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "message": "Please try again later"}

def create_app() -> FastAPI:
    return app