# 🌿 Basil

**Extremely easy AI-Powered search**

With just 1 command, Basil fetches your website data and creates a powerfull RAG search engine to use in your site.

Example: Imagine you have a website with 1000 pages, and you want to create a search engine that can answer questions like "What is the price of your services?" or "How can I contact support?". Basil will scrape your website, process the content using AI, and create a search engine that can answer these questions in seconds.


How does it work: 
1. **Scrape**: Basil scrapes your website and extracts the content.
2. **Process**: It processes the content using AI to create a searchable index, then places your example sentences in a chromaDb
3. **Search**: You can you use the build in endpoint `/search` to integrate in your website.

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](./docker-compose.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-green?logo=fastapi)](./basil-search/)
[![AI Powered](https://img.shields.io/badge/AI-Powered%20by%20Groq-orange)](./basil-search/src/utils/groq_client.py)

---

## 🚀 Quick Start

### One-Command Deployment

```bash
git clone https://github.com/basil-retriever/Basil
cd Basil
docker-compose up -d
curl -X POST http://localhost:3000/index?site=https://example.com

```

#### No Docker user?

```bash
git clone https://github.com/basil-retriever/Basil
cd Basil
docker-compose up -d
python3 basil-search/pipeline.py --url https://example.com --all 
```
`
**Access Points:**
- 🔍 **Search API**: `http://localhost:8000`
- 📊 **API Documentation**: `http://localhost:8000/docs`

### Local Development

```bash
cd basil-search
cp .env.example .env
# Add your GROQ_API_KEY to .env
docker-compose up --build
```

---

## 🏗️ Architecture

```
Basil Platform
├── 🔍 Search Engine (Port 8000)
│   ├── FastAPI REST Endpoints
│   ├── ChromaDB Vector Database
│   ├── Groq AI Processing
│   └── Content Management
│
└── 🎫 Document Services
    ├── Intent Detection
    └── Customer Request Processing
```

### Core Components

| Component | Description | Port | Technology |
|-----------|-------------|------|------------|
| **Basil Search** | AI-powered search and content processing | 8000 | FastAPI, ChromaDB, Groq |
| **Vector Database** | Semantic search and content storage | - | ChromaDB, SQLite |

---

## 🔧 Key Features

### 🌐 **Intelligent Website Processing**
- **Smart Scraping**: Extract content with automatic link discovery and rate limiting
- **Content Enrichment**: AI-generated search patterns and metadata
- **Multi-format Support**: Process HTML, markdown, and structured content

### 🔍 **Advanced Search Capabilities**
```bash
# Natural language search
curl "http://localhost:8000/search/query?q=website%20development%20pricing"

# Programmatic search
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "customer support services", "max_results": 10}'
```
## 🚀 Usage Examples

### Content Processing Pipeline

```bash
# 1. Scrape and process a website
cd basil-search
python pipeline.py --url https://example.com --all

# 2. Search the processed content
curl "http://localhost:8000/search/query?q=your%20search%20query"
---

## 🐳 Docker Configuration
### Full Stack Deployment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f basil-search
docker-compose logs -f n8n
```

### Individual Services
```bash
# Search engine only
cd basil-search
docker-compose up -d basil-search

# Workflows only  
docker-compose up -d n8n

# Production with Nginx
cd basil-search
docker-compose --profile production up -d
```

### Custom Website Processing
```bash
# Process specific website
cd basil-search
TARGET_URL=https://yourwebsite.com docker-compose --profile scraping run scraper
```

---

## ⚙️ Configuration

### Environment Setup

**Required Environment Variables:**
```bash
# Copy example configuration
cp basil-search/.env.example basil-search/.env

# Edit with your settings
GROQ_API_KEY=your_groq_api_key_here
```

### Service Configuration

| Variable | Service | Description | Required |
|----------|---------|-------------|----------|
| `GROQ_API_KEY` | Search | AI processing API key | ✅ |
---

## 📊 API Reference

### Search Endpoints

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| `GET` | `/` | API information | `curl localhost:8000/` |
| `POST` | `/search` | Semantic search | `{"query": "text", "max_results": 5}` |
| `GET` | `/search/query` | Search with params | `?q=search&max_results=5` |
| `GET` | `/health` | Health check | System status |
| `GET` | `/stats` | Database statistics | Collection info |

### Document Endpoints

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| `POST` | `/detect_intent` | Analyze intent | `{"text": "customer message"}` |
| `POST` | `/reload` | Reload database | Refresh vector store |

### Response Examples

**Search Response:**
```json
{
  "results": [
    {
      "content": "Website development services...",
      "metadata": {"source": "page.html", "section": "services"},
      "score": 0.95
    }
  ],
  "query": "website development",
  "total_results": 1
}
```

---

## 🛠️ Development

### Local Development Setup

```bash
# Clone and setup
git clone <repository-url>
cd Basil/basil-search

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Add your GROQ_API_KEY

# Run development server
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Run tests
cd basil-search
pytest tests/

# With coverage
pytest --cov=src tests/

# Test specific component
pytest tests/test_search_api.py -v
```

### Code Quality

```bash
# Format code
black src/
black routers/

# Lint code  
flake8 src/
flake8 routers/

# Type checking
mypy src/
```

---

## 🚨 Troubleshooting

### Common Issues

**❌ GROQ_API_KEY not found**
```bash
# Solution: Ensure .env file exists with your API key
cp basil-search/.env.example basil-search/.env
# Edit .env and add: GROQ_API_KEY=your_api_key_here
```

**❌ Docker build fails**
```bash
# Solution: Clean Docker cache and rebuild
docker system prune -a
docker-compose build --no-cache
```

**❌ ChromaDB connection issues**
```bash
# Solution: Reset database
rm -rf basil-search/chroma_db/
cd basil-search
python pipeline.py --load
```

**❌ N8N workflows not accessible**
```bash
# Solution: Check service status
docker-compose ps
docker-compose logs n8n
```

### Debug Mode

```bash
# Enable detailed logging
LOG_LEVEL=DEBUG python basil-search/pipeline.py --all

# Test individual components
cd basil-search
python pipeline.py --check-config
python pipeline.py --test-groq

# Health checks
curl http://localhost:8000/health
curl http://localhost:5678/healthz
```

---

## 📈 Performance & Scaling

### Performance Metrics
- **Scraping**: 1-2 pages/second with intelligent rate limiting
- **AI Processing**: 10-50 search patterns per page
- **Search Response**: Sub-second semantic search queries
- **Concurrent Users**: Handles 100+ simultaneous search requests

### Scaling Options
```bash
# Horizontal scaling with multiple instances
docker-compose up --scale basil-search=3

# Production deployment with load balancer
cd basil-search
docker-compose --profile production up -d
```

---

## 🌟 Use Cases

### 🏢 **Business Automation**
- **Content Management**: Searchable knowledge bases from websites
- **Lead Processing**: Extract and route customer requirements

### 🛒 **E-commerce Enhancement**
- **Product Search**: Semantic product discovery
- **Customer Service**: Automated response generation
- **Inventory Management**: Content-based product matching

### 📚 **Knowledge Management**
- **Documentation**: Searchable internal documentation
- **Research**: Academic paper and content analysis  
- **Training**: Interactive learning content discovery

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow existing code style and conventions
- Add tests for new functionality
- Update documentation for API changes
- Ensure Docker builds pass

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🌟 Star History

If you find Basil useful for your business automation needs, please consider giving it a star! ⭐

---

**Built with**: Python, FastAPI, ChromaDB, Groq AI, N8N, Docker

*Basil - Transforming websites into intelligent business automation platforms* 🌿