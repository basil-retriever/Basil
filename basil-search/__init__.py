"""
Basil - AI-Powered Website Search Engine
"""

__version__ = "1.0.0"
__author__ = "Basil Team"
__email__ = "team@basil-retriever.com"
__description__ = "AI-Powered Website Search Engine with ChromaDB and Groq"

from .app import app
from .pipeline import main as pipeline_main

__all__ = ["app", "pipeline_main", "__version__"]