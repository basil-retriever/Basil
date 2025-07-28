# 🌿 Basil Search

AI-Powered Website Content Scraper & Semantic Search Engine

Transform any website into a searchable knowledge base with AI-generated search patterns and vector similarity matching.

## 🚀 Quick Start

### Docker Deployment (Recommended)

```bash
git clone <repository-url>
cd basil-search
cp .env.example .env
# Add your GROQ_API_KEY to .env

docker-compose up --build
```

The API will be available at `http://localhost:8000`

### Local Development

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env

python pipeline.py --url https://example.com --all
```

## 🌟 Features

- **🌐 Intelligent Website Scraping** - Extract content with automatic link discovery
- **🤖 AI-Powered Processing** - Generate search sentences using Groq API
- **🔍 Semantic Search** - Vector-based similarity search with ChromaDB
- **⚡ REST API** - FastAPI endpoints for search functionality
- **🐳 Docker Ready** - Complete containerization for easy deployment
- **📊 Real-time Analytics** - Search statistics and health monitoring

## 🔧 Usage

### One-Click Website Indexing

```bash
# Scrape, process, and start search API
python pipeline.py --url https://example.com --all

# Step by step
python pipeline.py --url https://example.com --scrape
python pipeline.py --process --load
python pipeline.py --serve
```

### Docker Commands

```bash
# Production deployment with Nginx
docker-compose --profile production up -d

# Run scraping job
TARGET_URL=https://example.com docker-compose --profile scraping run scraper

# Just the search service
docker-compose up -d basil-search
```

### Search Examples

```bash
# Search via GET
curl "http://localhost:8000/search/query?q=website%20development&max_results=5"

# Search via POST
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "website development", "max_results": 5}'

# Health check
curl "http://localhost:8000/health"
```

## 🏗️ Architecture

```
basil-search/
├── src/                    # Source code
│   ├── api/               # FastAPI endpoints
│   ├── database/          # ChromaDB management
│   ├── processors/        # AI content processing
│   ├── scrapers/          # Website scraping
│   └── utils/             # Utility functions
├── data/                  # Data storage
│   ├── scraped_pages/    # Raw scraped content
│   └── processed/        # AI-processed files
├── chroma_db/            # Vector database
├── docs/                 # Documentation
├── pipeline.py           # Main automation script
├── docker-compose.yml    # Docker configuration
└── Dockerfile           # Container definition
```

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| POST | `/search` | Semantic search with JSON |
| GET | `/search/query` | Search with query params |
| GET | `/health` | Health check |
| GET | `/stats` | Collection statistics |
| POST | `/reload` | Reload database |

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for AI processing | Yes |
| `TARGET_URL` | Website URL to scrape | For scraping |
| `API_HOST` | Server host address | No |
| `API_PORT` | Server port number | No |

### Docker Services

| Service | Purpose | Port |
|---------|---------|------|
| `basil-search` | Main search API | 8000 |
| `nginx` | Reverse proxy | 80, 443 |
| `scraper` | Website scraping job | - |

## 🔍 How It Works

1. **🌐 Website Scraping**: Extract content from any website with intelligent link discovery
2. **🤖 AI Processing**: Generate natural language search patterns using Groq API
3. **📊 Vector Storage**: Store content and search patterns in ChromaDB
4. **🔍 Semantic Search**: Match user queries with content using vector similarity

### Example Workflow

```bash
# Input: Website URL
https://example.com

# Output: Searchable knowledge base
"How do I build a website?" → matches content about web development
"I need hosting services" → matches content about web hosting
"Website pricing information" → matches content about costs
```

## 🔧 Advanced Usage

### Custom Pipeline Configuration

```bash
# Check configuration
python pipeline.py --check-config

# Test AI connection
python pipeline.py --test-groq

# Custom scraping
python pipeline.py --url https://example.com --scrape --max-pages 100

# Process existing content
python pipeline.py --process --load
```

### Python API

```python
from src.scrapers import WebsiteScraper
from src.processors import ContentProcessor
from src.database import ChromaManager

# Scrape website
scraper = WebsiteScraper("https://example.com")
results = scraper.scrape_website()

# Process content
processor = ContentProcessor()
processed = processor.process_all()

# Search content
chroma = ChromaManager()
results = chroma.search("your query", n_results=10)
```

## 🐳 Docker Profiles

### Development
```bash
docker-compose up basil-search
```

### Production
```bash
docker-compose --profile production up -d
```

### Scraping Jobs
```bash
TARGET_URL=https://example.com docker-compose --profile scraping run scraper
```

## 📚 Documentation

- **Full Documentation**: Open `docs/index.html` in your browser
- **API Documentation**: Visit `http://localhost:8000/docs` when server is running
- **Health Monitoring**: Visit `http://localhost:8000/health`

## 🛠️ Development

### Setup Development Environment

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY

python pipeline.py --check-config
python pipeline.py --test-groq
```

### Running Tests

```bash
pytest tests/
pytest --cov=src tests/
```

### Code Quality

```bash
black src/
flake8 src/
```

## 🚨 Troubleshooting

### Common Issues

**GROQ_API_KEY not found**
```bash
# Ensure .env file exists with your API key
cp .env.example .env
# Edit .env and add: GROQ_API_KEY=your_api_key_here
```

**Docker build fails**
```bash
# Clean Docker cache
docker system prune -a
docker-compose build --no-cache
```

**ChromaDB connection issues**
```bash
# Reset database
rm -rf chroma_db/
python pipeline.py --load
```

### Debug Mode

```bash
# Enable debug logging
LOG_LEVEL=DEBUG python pipeline.py --url https://example.com --all

# Test individual components
python pipeline.py --check-config
python pipeline.py --test-groq
```

## 📈 Performance

- **Scraping**: ~1-2 pages per second with rate limiting
- **Processing**: ~10-50 sentences per page (AI-generated)
- **Search**: Sub-second response times for similarity queries
- **Storage**: Efficient vector storage with ChromaDB

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Built with**: Python, FastAPI, ChromaDB, Groq AI, Docker