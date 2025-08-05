# 🌿 Basil

**AI-Powered Website Search Engine**

Transform any website into a powerful, searchable knowledge base with just one command. Basil scrapes, processes, and creates intelligent search endpoints for your content.

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](./docker-compose.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-green?logo=fastapi)](./basil-search/)
[![AI Powered](https://img.shields.io/badge/AI-Powered%20by%20Groq-orange)]()

---

## 🚀 Getting Started

### Prerequisites

Create a `.env` file with your Groq API key nd allowed origins:
```bash
GROQ_API_KEY=your_groq_api_key_here
ALLOWED_ORIGINS=*
```

### 📦 Installation Options

#### Option 1: Pip Install (Recommended)
```bash
# Install latest version
pip install git+https://github.com/basil-retriever/Basil.git

# OR  Install specific version
pip install git+https://github.com/basil-retriever/Basil.git@v0.1.0

# Create .env file with your Groq API key and CORS origins
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
echo "ALLOWED_ORIGINS=*" >> .env

# Process a public website
python -m basil_search.pipeline --url https://example.com --all

# OR Process a internal or dev website
python -m basil_search.pipeline --url http:/localhost:4200 --process --internal
```

#### Option 2: Docker
```bash
git clone https://github.com/basil-retriever/Basil
   ```
1. **Build and run the Docker container:**
   ```bash
   docker build -t basil:latest .
   docker run -p 8000:8000 basil:latest
   ```

2. **Access the setup page:**
   Open your browser and go to `http://localhost:8000`

3. **Configure Basil:**
   - Enter your Groq API key
   - Provide the website URL you want to index
   - Configure allowed origins (CORS) * for any
   - Set maximum pages to index
   - Check "Internal/Development Site" if indexing localhost or private networks

4. **Start indexing:**
   Click "Start Indexing" and wait for the process to complete

# Process a website
curl -X GET "http://localhost:8000/index?site=https://example.com"
```

---
## local Development or contributions
1. Fork this repo
2. Do your changes
3. `pip install -e .`
4. Go to a test project and create a virtual environment ` python -m venv venv`
5. `source venv/bin/activate`  On Windows: `venv\Scripts\activate`
7. go out the virtual environment and install basil in editable mode
6. pip install -e /path/to/basil

## 📡 API Endpoints

### Search Endpoints

#### `POST /ask`
Ask questions about indexed content.

**Request:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What services do you offer?", "max_results": 5}'
```

**Response:**
```json
{
  "question": "What services do you offer?",
  "answer": "We offer web development, AI integration, and search optimization services..."
}
```

#### `POST /detect_intent`
Detect intent from user messages.

**Request:**
```bash
curl -X POST "http://localhost:8000/detect_intent" \
  -H "Content-Type: application/json" \
  -d '{"text": "I want to buy a ticket"}'
```

**Response:**
```json
{
  "intent": "purchase_ticket",
  "score": 0.95,
  "extracted_info": {}
}
```

### Indexing Endpoints

#### `GET /index`
Index a public website.

**Request:**
```bash
curl -X GET "http://localhost:8000/index?site=https://example.com"
```

**Response:**
```json
{
  "message": "Site indexing started for https://example.com",
  "status": "accepted",
  "site": "https://example.com"
}
```

#### `POST /index-internal`
Index internal/localhost sites with authentication.

**Request:**
```bash
curl -X POST "http://localhost:8000/index-internal" \
  -H "Content-Type: application/json" \
  -d '{
    "site": "http://localhost:4200",
    "max_pages": 50,
    "auth_token": "Bearer your-token",
    "custom_headers": {
      "X-API-Key": "dev-key-123"
    }
  }'
```

**Response:**
```json
{
  "message": "Internal site indexing started for http://localhost:4200",
  "status": "accepted",
  "site": "http://localhost:4200",
  "max_pages": 50,
  "type": "internal"
}
```

### Documentation

#### `GET /docs`
Interactive API documentation (Swagger UI).

**Request:**
```bash
curl http://localhost:8000/docs
```

**Response:**
HTML page with interactive API documentation.

---

## 🔧 Local Development CLI

If you're working with the source code, use the local CLI:

```bash
git clone https://github.com/basil-retriever/Basil
cd Basil

# Make CLI executable
chmod +x basil

# Check status
./basil status

# Start server
./basil server

# Run pipeline
./basil pipeline --url https://example.com --all

# Show help
./basil help
```

---

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with**: Python, FastAPI, ChromaDB, Groq AI, Docker