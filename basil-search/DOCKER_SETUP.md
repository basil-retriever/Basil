# Basil Docker Setup

This document explains how to use the Basil Docker container with the new setup page.

## Quick Start

1. **Build and run the Docker container:**
   ```bash
   cd basil-search
   docker build -t basil:latest .
   docker run -p 8000:8000 basil:latest
   ```

2. **Access the setup page:**
   Open your browser and go to `http://localhost:8000`

3. **Configure Basil:**
   - Enter your Groq API key
   - Provide the website URL you want to index
   - Configure allowed origins (CORS)
   - Set maximum pages to index
   - Check "Internal/Development Site" if indexing localhost or private networks

4. **Start indexing:**
   Click "Start Indexing" and wait for the process to complete

## What Happens During Setup

1. **Configuration Storage**: Your settings are saved to `.env` and `basil_config.json` files
2. **API Key Validation**: The Groq API key is tested for connectivity
3. **Background Indexing**: The website scraping, processing, and database loading happens in the background
4. **Automatic Redirect**: Once complete, you'll be redirected to the API documentation

## Configuration Files Created

- **`.env`**: Contains environment variables (Groq API key, CORS settings)
- **`basil_config.json`**: Contains setup configuration and indexing status

## API Endpoints After Setup

- **`/docs`**: Interactive API documentation (Swagger UI)
- **`/ask`**: Ask questions about your indexed content
- **`/search`**: Search through your indexed content
- **`/setup/status`**: Check setup and indexing status

## Directory Structure

```
/app/
├── data/
│   ├── scraped_pages/    # Raw scraped website content
│   └── processed/        # AI-processed content
├── chroma_db/           # Vector database files
├── .env                # Environment configuration
└── basil_config.json   # Setup configuration
```

## Troubleshooting

### Setup Page Not Loading
- Ensure the container is running: `docker ps`
- Check container logs: `docker logs <container_id>`

### Indexing Failed
- Check the setup status: `GET /setup/status`
- Verify your Groq API key is valid
- Ensure the website URL is accessible

### Permission Issues
- Make sure the container has write permissions for data directories
- For internal sites, ensure network connectivity from container

## Environment Variables

You can also set these environment variables when running the container:

```bash
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_key_here \
  -e ALLOWED_ORIGINS="*" \
  basil:latest
```

## Using Docker Compose

Create a `docker-compose.yml`:

```yaml
version: '3.8'
services:
  basil:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - ALLOWED_ORIGINS=*
    volumes:
      - ./data:/app/data
      - ./chroma_db:/app/chroma_db
```

Then run: `docker-compose up -d`