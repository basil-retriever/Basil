from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import os
import requests

router = APIRouter()

class AskRequest(BaseModel):
    question: str

try:
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    raise RuntimeError(f"Failed to load embedding model: {e}")

@router.post("/ask")
def ask_question(req: AskRequest):
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        return JSONResponse(status_code=500, content={"error": "Missing GROQ_API_KEY environment variable."})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [{"role": "user", "content": req.question}]
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        answer = result["choices"][0]["message"]["content"]
        return {"question": req.question, "answer": answer}
    except requests.exceptions.HTTPError:
        return JSONResponse(status_code=response.status_code, content={"error": f"HTTP error: {response.text}"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Unexpected response structure from Groq API: {str(e)}"})
