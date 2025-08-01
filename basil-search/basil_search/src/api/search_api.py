from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import os
import requests
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

class AskRequest(BaseModel):
    question: str
    max_context_results: Optional[int] = 5

class AskResponse(BaseModel):
    question: str
    answer: str
    context_sources: List[SearchResult]
    processing_time: Optional[float] = None

@app.get("/")
async def root():
    return {
        "message": "Website Search API",
        "version": "1.0.0",
        "endpoints": {
            "/search": "POST - Semantic search",
            "/search/query": "GET - Search with query parameter",
            "/ask": "POST - RAG-powered question answering",
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

@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    try:
        import time
        start_time = time.time()
        
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Get GROQ API key
        GROQ_API_KEY = Config.GROQ_API_KEY
        if not GROQ_API_KEY:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")
        
        # First, perform semantic search to get relevant context
        search_results = chroma_manager.search(
            query=request.question,
            n_results=request.max_context_results
        )
        
        # Build context from search results
        context_texts = []
        context_sources = []
        
        for result in search_results['results']:
            context_texts.append(f"Source: {result['metadata'].get('title', 'Unknown')}\n{result['document']}")
            context_sources.append(SearchResult(
                document=result['document'],
                metadata=result['metadata'],
                similarity=result['similarity'],
                distance=result['distance']
            ))
        
        # Create RAG prompt
        context = "\n\n---\n\n".join(context_texts)
        rag_prompt = f"""Based on the following context from the website, answer the user's question. If the context doesn't contain enough information to answer the question, say so clearly.

Context:
{context}

Question: {request.question}

Answer:"""
        
        # Call Groq API
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": Config.GROQ_MODEL,
            "messages": [{"role": "user", "content": rag_prompt}],
            "max_tokens": 1000
        }
        
        response = requests.post(
            Config.GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Groq API error: {response.status_code}")
        
        result = response.json()
        answer = result["choices"][0]["message"]["content"]
        
        processing_time = time.time() - start_time
        
        return AskResponse(
            question=request.question,
            answer=answer,
            context_sources=context_sources,
            processing_time=processing_time
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Groq API request error: {e}")
        raise HTTPException(status_code=500, detail=f"AI service unavailable: {str(e)}")
    except Exception as e:
        logger.error(f"Ask error: {e}")
        raise HTTPException(status_code=500, detail=f"Ask failed: {str(e)}")

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