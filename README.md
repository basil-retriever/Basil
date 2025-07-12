# 🌿 Basil

**AI-Powered Business Automation Platform**

Transform websites into intelligent, searchable knowledge bases with automated ticket generation and workflow orchestration.

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
```

**Access Points:**
- 🔍 **Search API**: `http://localhost:8000`
- 🎫 **Ticket Generation**: `http://localhost:8000/generate-ticket`
- 🤖 **Workflow Automation**: `http://localhost:5678`
- 📊 **API Documentation**: `http://localhost:8000/docs`

### Local Development

```bash
cd basil-search
cp .env.example .env
# Add your GROQ_API_KEY to .env
docker-compose up --build
```

---

## 🌟 What is Basil?

Basil is a comprehensive business automation platform that combines:

### 🧠 **Intelligent Content Processing**
- **Website Scraping**: Automatically extract and process website content
- **AI-Powered Analysis**: Generate searchable content using advanced language models
- **Semantic Search**: Find relevant information using natural language queries

### 🎫 **Automated Ticket Generation** 
- **Intent Detection**: Automatically identify customer requests and requirements
- **PDF Generation**: Create professional tickets and documents
- **Smart Routing**: Route requests based on content analysis

### 🔄 **Workflow Orchestration**
- **N8N Integration**: Visual workflow builder for complex automation
- **API Orchestration**: Connect multiple services and external APIs
- **Event-Driven Processing**: React to triggers and automate responses

---

## 🏗️ Architecture

```
Basil Platform
├── 🌐 Web Interface (Port 5678)
│   ├── N8N Workflow Engine
│   ├── Visual Automation Builder
│   └── External API Integrations
│
├── 🔍 Search Engine (Port 8000)
│   ├── FastAPI REST Endpoints
│   ├── ChromaDB Vector Database
│   ├── Groq AI Processing
│   └── Content Management
│
└── 🎫 Document Services
    ├── PDF Ticket Generation
    ├── Intent Detection
    └── Customer Request Processing
```

### Core Components

| Component | Description | Port | Technology |
|-----------|-------------|------|------------|
| **Basil Search** | AI-powered search and content processing | 8000 | FastAPI, ChromaDB, Groq |
| **N8N Workflows** | Visual automation and workflow orchestration | 5678 | N8N.io |
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

### 🎫 **Automated Document Generation**
```bash
# Generate PDF tickets
curl -X POST "http://localhost:8000/generate-ticket" \
  -H "Content-Type: application/json" \
  -d '{"text": "I need a website for my restaurant", "customer_name": "John Doe"}'
```

### 🤖 **Workflow Automation**
- **Visual Builder**: Create complex workflows using N8N's drag-and-drop interface
- **API Integration**: Connect to external services and APIs
- **Event Triggers**: Automate responses to webhooks, schedules, and data changes

---

## 🚀 Usage Examples

### Content Processing Pipeline

```bash
# 1. Scrape and process a website
cd basil-search
python pipeline.py --url https://example.com --all

# 2. Search the processed content
curl "http://localhost:8000/search/query?q=your%20search%20query"

# 3. Generate tickets from search results
curl -X POST "http://localhost:8000/generate-ticket" \
  -H "Content-Type: application/json" \
  -d '{"text": "search result content", "customer_name": "Customer"}'
```

### Workflow Automation Example

1. **Visit**: `http://localhost:5678`
2. **Create Workflow**: Use the visual editor to build automation
3. **Connect Services**: Link Basil Search API with external tools
4. **Deploy**: Activate workflows for automatic processing

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
TARGET_URL=https://website-to-process.com
API_HOST=0.0.0.0
API_PORT=8000
```

### Service Configuration

| Variable | Service | Description | Required |
|----------|---------|-------------|----------|
| `GROQ_API_KEY` | Search | AI processing API key | ✅ |
| `TARGET_URL` | Scraper | Website to process | For scraping |
| `GENERIC_TIMEZONE` | N8N | Workflow timezone | No |

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
| `POST` | `/generate-ticket` | Create PDF ticket | `{"text": "content", "customer_name": "name"}` |
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

**Ticket Generation Response:**
```json
{
  "status": "success",
  "ticket_id": "TICKET_20240101_001",
  "pdf_path": "/path/to/ticket.pdf",
  "details": {
    "customer_name": "John Doe",
    "detected_intent": "website_development",
    "estimated_cost": "$2,500"
  }
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
- **Customer Support**: Automatic ticket generation from inquiries
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