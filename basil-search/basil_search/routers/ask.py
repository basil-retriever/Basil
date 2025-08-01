from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time
import logging
import requests
from basil_search.src.database import ChromaManager
from basil_search.src.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class AskRequest(BaseModel):
    question: str
    max_context_results: Optional[int] = 5

class SearchResult(BaseModel):
    document: str
    metadata: Dict[str, Any]
    similarity: float
    distance: float

class AskResponse(BaseModel):
    question: str
    answer: str
    context_sources: List[SearchResult]
    processing_time: Optional[float] = None

# Initialize ChromaDB manager
try:
    chroma_manager = ChromaManager()
except Exception as e:
    logger.error(f"Failed to initialize ChromaDB: {e}")
    chroma_manager = None

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    if not chroma_manager:
        raise HTTPException(status_code=500, detail="Database not available. Please check ChromaDB setup.")
    
    try:
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
        if context_texts:
            context = "\n\n---\n\n".join(context_texts)
            rag_prompt = f"""Based on the following context from the website, answer the user's question. If the context doesn't contain enough information to answer the question, say so clearly.

Context:
{context}

Question: {request.question}

Answer:"""
        else:
            # Fallback if no context found
            rag_prompt = f"""I don't have any relevant context from the scraped website content to answer your question. 

Question: {request.question}

Please note: No relevant content was found in the database. You may need to scrape and process website content first, or the question might be outside the scope of the available content."""
        
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
