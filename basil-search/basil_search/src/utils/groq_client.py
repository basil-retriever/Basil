import requests
import json
from typing import Optional, Dict, Any
import logging
from basil_search.src.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.GROQ_API_KEY
        self.api_url = Config.GROQ_API_URL
        self.model = Config.GROQ_MODEL
        
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found. Client will not function properly.")
    
    def generate_text(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        if not self.api_key:
            raise Exception("GROQ_API_KEY not configured")
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                error_msg = f"Groq API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def generate_search_sentences(self, title: str, url: str, content: str, num_sentences: int = 10) -> list:
        prompt = f"""
Based on the following website content, generate {num_sentences} example sentences that users might search for or ask about when looking for this information.

Website Title: {title}
Website URL: {url}
Content: {content[:1000]}...

Generate sentences in natural language that would lead users to this specific page. Focus on:
- Questions users might ask
- Problems they're trying to solve
- Services they're looking for
- Information they need

Return only the sentences, one per line, without numbers or bullet points.
"""
        
        response = self.generate_text(prompt)
        
        sentences = []
        for line in response.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 10:
                import re
                line = re.sub(r'^[-*•\d\.\)\s]+', '', line).strip()
                if line:
                    sentences.append(line)
        
        return sentences[:num_sentences]
    
    def test_connection(self) -> bool:
        try:
            response = self.generate_text("Hello, this is a test message.")
            return len(response) > 0
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False