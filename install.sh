#!/bin/bash
set -e

# Basil Installation Script
# This script installs Basil and sets up the environment

echo "🌿 Installing Basil - AI-Powered Website Search Engine"
echo "=================================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version detected (>= 3.8 required)"
else
    echo "❌ Python 3.8+ required. Found: $python_version"
    exit 1
fi

# Install package
echo "📦 Installing Basil package..."
pip3 install -e .

# Create .env file if it doesn't exist
if [ ! -f "basil-search/.env" ]; then
    echo "⚙️  Creating environment configuration..."
    cp basil-search/.env.example basil-search/.env 2>/dev/null || {
        cat > basil-search/.env << EOF
# Basil Configuration
GROQ_API_KEY=your_groq_api_key_here
LOG_LEVEL=INFO
CHROMA_DB_PATH=./chroma_db
EOF
    }
    echo "📝 Please edit basil-search/.env and add your GROQ_API_KEY"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Quick Start:"
echo "1. Edit basil-search/.env and add your GROQ_API_KEY"
echo "2. Run: basil-pipeline --url https://example.com --all"
echo "3. Start server: basil-server"
echo "4. Access API at: http://localhost:8000"
echo ""
echo "For Docker deployment:"
echo "  docker-compose up -d"
echo ""
echo "Documentation: https://github.com/basil-retriever/Basil#readme"