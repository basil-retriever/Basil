"""
Basil - AI-Powered Website Search Engine
"""

try:
    from ._version import version as __version__
except ImportError:
    # Fallback for development installations
    try:
        from importlib.metadata import version
        __version__ = version("basil-search")
    except ImportError:
        __version__ = "unknown"

__author__ = "Basil Team"
__email__ = "team@basil-retriever.com"
__description__ = "AI-Powered Website Search Engine with ChromaDB and Groq"

from .app import app
from .pipeline import main as pipeline_main

__all__ = ["app", "pipeline_main", "__version__"]