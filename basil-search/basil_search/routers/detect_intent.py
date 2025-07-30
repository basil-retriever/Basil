from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import re
import chromadb
from sentence_transformers import SentenceTransformer

try:
    import spacy
except ImportError:
    spacy = None

router = APIRouter()

class TextInput(BaseModel):
    text: str

try:
    nlp = spacy.load("en_core_web_sm") if spacy else None
except (OSError, AttributeError):
    nlp = None

try:
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    intent_collection = chroma_client.get_collection(name="ticket_intent_collection")
except Exception as e:
    raise RuntimeError(f"Failed to load ChromaDB collection: {e}. Please ensure 'chroma_data.py' was run successfully.")

try:
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    raise RuntimeError(f"Failed to load embedding model: {e}")

@router.post("/detect_intent")
def detect_intent(input: TextInput):
    text = input.text

    if not text:
        return {"intent": "no_text", "score": 0.0, "extracted_info": {}}

    extracted_info = {}

    try:
        query_embedding = embedding_model.encode(text).tolist()
        results = intent_collection.query(
            query_embeddings=[query_embedding],
            n_results=1,
            include=['metadatas', 'distances']
        )

        detected_intent = "unknown"
        similarity_score = 0.0

        if results and results['metadatas'] and results['metadatas'][0]:
            closest_match_metadata = results['metadatas'][0][0]
            distance = results['distances'][0][0]
            similarity_score = 1 - distance
            detected_intent = closest_match_metadata.get("intent", "unknown")

        if similarity_score < 0.6:
            detected_intent = "unsure_or_unknown"

        if nlp and detected_intent == "purchase_ticket":
            doc = nlp(text)
            names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
            extracted_info["names"] = names

            ticket_count = None
            numbers = re.findall(r'\b\d+\b', text)

            if numbers:
                try:
                    ticket_count = int(numbers[0])
                except ValueError:
                    ticket_count = None

            words_to_numbers = {
                "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
            }
            for word in text.lower().split():
                if word in words_to_numbers and ticket_count is None:
                    ticket_count = words_to_numbers[word]
                    break

            extracted_info["ticket_count"] = ticket_count if ticket_count is not None else "undetected"

        return {"intent": detected_intent, "score": similarity_score, "extracted_info": extracted_info}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"An error occurred during intent detection: {str(e)}"})
