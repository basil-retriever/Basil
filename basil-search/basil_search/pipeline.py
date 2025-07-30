#!/usr/bin/env python3
"""
Website Content Scraper Pipeline
=================================

Complete pipeline for scraping websites, processing content, and setting up
semantic search capabilities.

This script provides a one-click solution to:
1. Scrape a website and extract content
2. Process content with AI-powered search sentence generation
3. Load everything into ChromaDB for semantic search
4. Start the search API server

Usage:
    python pipeline.py --url https://example.com --scrape --process --load --serve
    python pipeline.py --url https://example.com --all  # Run all steps
    python pipeline.py --serve  # Just start the API server
"""

import argparse
import sys
import time
from pathlib import Path
import logging
from typing import Optional

from basil_search.src.config import Config
from basil_search.src.scrapers import scrape_website
from basil_search.src.scrapers.internal_scraper import scrape_internal_website
from basil_search.src.processors import process_scraped_content
from basil_search.src.database import setup_chromadb
from basil_search.src.utils import GroqClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebsitePipeline:
    """
    Main pipeline class for orchestrating the entire workflow.
    """
    
    def __init__(self):
        """Initialize the pipeline."""
        self.config = Config()
        self.config.setup_directories()
        
        # Validate configuration
        if not self.config.validate():
            logger.warning("Configuration validation failed. Some features may not work.")
    
    def scrape_website(self, url: str, max_pages: int = 50) -> dict:
        """
        Scrape a website and extract content.
        
        Args:
            url: Website URL to scrape
            max_pages: Maximum number of pages to scrape
            
        Returns:
            Dictionary with scraping results
        """
        logger.info(f"Starting website scraping: {url}")
        
        try:
            results = scrape_website(url, max_pages)
            logger.info(f"Scraping completed: {results}")
            return results
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise
    
    def scrape_internal_website(self, url: str, max_pages: int = 50) -> dict:
        """
        Scrape an internal website (localhost, private networks) with authentication support.
        
        Args:
            url: Internal website URL to scrape
            max_pages: Maximum number of pages to scrape
            
        Returns:
            Dictionary with scraping results
        """
        logger.info(f"Starting internal website scraping: {url}")
        
        try:
            results = scrape_internal_website(url, max_pages)
            logger.info(f"Internal scraping completed: {results}")
            return results
        except Exception as e:
            logger.error(f"Internal scraping failed: {e}")
            raise
    
    def process_content(self) -> dict:
        """
        Process scraped content and generate search sentences.
        
        Returns:
            Dictionary with processing results
        """
        logger.info("Starting content processing...")
        
        try:
            results = process_scraped_content()
            logger.info(f"Processing completed: {results}")
            return results
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise
    
    def load_database(self) -> dict:
        """
        Load processed content into ChromaDB.
        
        Returns:
            Dictionary with loading results
        """
        logger.info("Starting database loading...")
        
        try:
            chroma_manager = setup_chromadb()
            results = chroma_manager.load_processed_files()
            logger.info(f"Database loading completed: {results}")
            return results
        except Exception as e:
            logger.error(f"Database loading failed: {e}")
            raise
    
    def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Start the FastAPI server.
        
        Args:
            host: Server host
            port: Server port
        """
        logger.info(f"Starting server on {host}:{port}")
        
        try:
            import uvicorn
            from app import app
            
            uvicorn.run(
                app,
                host=host,
                port=port,
                reload=False,
                access_log=True
            )
        except Exception as e:
            logger.error(f"Server failed to start: {e}")
            raise
    
    def run_pipeline(self, url: Optional[str] = None, max_pages: int = 50, 
                    scrape: bool = False, process: bool = False, 
                    load: bool = False, serve: bool = False, internal: bool = False):
        """
        Run the complete pipeline or specified steps.
        
        Args:
            url: Website URL (required for scraping)
            max_pages: Maximum pages to scrape
            scrape: Whether to scrape the website
            process: Whether to process content
            load: Whether to load into database
            serve: Whether to start the server
            internal: Whether to use internal scraper (for localhost/private networks)
        """
        results = {}
        
        # Step 1: Scrape website
        if scrape:
            if not url:
                raise ValueError("URL is required for scraping")
            
            if internal:
                logger.info("Using internal scraper for localhost/private network")
                results['scraping'] = self.scrape_internal_website(url, max_pages)
            else:
                results['scraping'] = self.scrape_website(url, max_pages)
        
        # Step 2: Process content
        if process:
            results['processing'] = self.process_content()
        
        # Step 3: Load into database
        if load:
            results['loading'] = self.load_database()
        
        # Step 4: Start server
        if serve:
            logger.info("Pipeline completed. Starting server...")
            self.start_server()
        
        return results

def main():
    """Main entry point for the pipeline."""
    parser = argparse.ArgumentParser(
        description="Website Content Scraper Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape a website and process everything
  python pipeline.py --url https://example.com --all
  
  # Just scrape a website
  python pipeline.py --url https://example.com --scrape
  
  # Process existing scraped content
  python pipeline.py --process --load
  
  # Start the API server
  python pipeline.py --serve
  
  # Custom workflow
  python pipeline.py --url https://example.com --scrape --process --load --serve
        """
    )
    
    # URL and scraping options
    parser.add_argument(
        "--url",
        type=str,
        help="Website URL to scrape"
    )
    
    parser.add_argument(
        "--max-pages",
        type=int,
        default=50,
        help="Maximum number of pages to scrape (default: 50)"
    )
    
    parser.add_argument(
        "--internal",
        action="store_true",
        help="Internal site mode (allows localhost, private IPs, custom auth)"
    )
    
    # Pipeline steps
    parser.add_argument(
        "--scrape",
        action="store_true",
        help="Scrape the website"
    )
    
    parser.add_argument(
        "--process",
        action="store_true",
        help="Process scraped content"
    )
    
    parser.add_argument(
        "--load",
        action="store_true",
        help="Load content into ChromaDB"
    )
    
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start the API server"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all steps (scrape, process, load, serve)"
    )
    
    # Server options
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Server host (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port (default: 8000)"
    )
    
    # Other options
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Check configuration and exit"
    )
    
    parser.add_argument(
        "--test-groq",
        action="store_true",
        help="Test Groq API connection and exit"
    )
    
    args = parser.parse_args()
    
    # Handle special options
    if args.check_config:
        config = Config()
        if config.validate():
            print("✓ Configuration is valid")
            sys.exit(0)
        else:
            print("✗ Configuration validation failed")
            sys.exit(1)
    
    if args.test_groq:
        try:
            client = GroqClient()
            if client.test_connection():
                print("✓ Groq API connection successful")
                sys.exit(0)
            else:
                print("✗ Groq API connection failed")
                sys.exit(1)
        except Exception as e:
            print(f"✗ Groq API test failed: {e}")
            sys.exit(1)
    
    # Handle --all flag
    if args.all:
        args.scrape = True
        args.process = True
        args.load = True
        args.serve = True
    
    # Validate arguments
    if not any([args.scrape, args.process, args.load, args.serve]):
        parser.error("At least one action must be specified (--scrape, --process, --load, --serve, or --all)")
    
    if args.scrape and not args.url:
        parser.error("--url is required when using --scrape")
    
    try:
        # Initialize pipeline
        pipeline = WebsitePipeline()
        
        # Run pipeline
        results = pipeline.run_pipeline(
            url=args.url,
            max_pages=args.max_pages,
            scrape=args.scrape,
            process=args.process,
            load=args.load,
            serve=args.serve,
            internal=args.internal
        )
        
        # Print results if not serving
        if not args.serve and results:
            print("\n" + "="*50)
            print("PIPELINE RESULTS")
            print("="*50)
            for step, result in results.items():
                print(f"\n{step.upper()}:")
                for key, value in result.items():
                    print(f"  {key}: {value}")
    
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()