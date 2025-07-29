import requests
import os
import json
from typing import Optional, Dict, Any
import logging
from urllib.parse import urlparse
from .website_scraper import WebsiteScraper
from ..config import Config

logger = logging.getLogger(__name__)

class InternalWebsiteScraper(WebsiteScraper):
    """
    Enhanced scraper for internal sites with authentication support.
    
    Supports:
    - Basic authentication
    - Bearer token authentication  
    - Custom headers
    - Localhost and private network URLs
    - Relaxed SSL verification for development
    """
    
    def __init__(self, base_url: str, output_dir=None, max_pages: int = 50, **kwargs):
        super().__init__(base_url, output_dir, max_pages)
        
        # Setup authentication from environment variables
        self.session = requests.Session()
        self._setup_authentication()
        self._setup_internal_config()
        
    def _setup_authentication(self):
        """Setup authentication headers from environment variables"""
        
        # Bearer token authentication
        auth_token = os.getenv('BASIL_AUTH_TOKEN')
        if auth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })
            logger.info("Added Bearer token authentication")
        
        # Custom authorization header
        auth_header = os.getenv('BASIL_AUTH_HEADER')
        if auth_header:
            self.session.headers.update({
                'Authorization': auth_header
            })
            logger.info("Added custom authorization header")
        
        # Custom headers (JSON format)
        custom_headers = os.getenv('BASIL_CUSTOM_HEADERS')
        if custom_headers:
            try:
                headers_dict = json.loads(custom_headers)
                self.session.headers.update(headers_dict)
                logger.info(f"Added custom headers: {list(headers_dict.keys())}")
            except json.JSONDecodeError:
                logger.warning("Invalid JSON in BASIL_CUSTOM_HEADERS, ignoring")
    
    def _setup_internal_config(self):
        """Setup configuration for internal sites"""
        
        # Add common development headers
        self.session.headers.update({
            'User-Agent': 'Basil-Internal-Scraper/1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Disable SSL verification for localhost (development only)
        parsed_url = urlparse(self.base_url)
        if parsed_url.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
            self.session.verify = False
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            logger.info("Disabled SSL verification for localhost")
    
    def scrape_page(self, url: str) -> bool:
        """
        Enhanced page scraping with authentication support
        """
        try:
            # Use the configured session instead of direct requests
            response = self.session.get(url, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            markdown_content = self.html_to_markdown(response.text, url)
            
            filename = self._generate_filename(url)
            filepath = self.output_dir / f"{filename}.md"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Scraped internal: {url} -> {filepath}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to scrape internal site {url}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error scraping internal site {url}: {e}")
            return False
    
    def discover_links(self, url: str) -> list:
        """
        Enhanced link discovery with authentication
        """
        discovered_urls = []
        
        try:
            response = self.session.get(url, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Handle relative URLs
                from urllib.parse import urljoin
                full_url = urljoin(url, href)
                parsed_url = urlparse(full_url)
                
                # More flexible domain matching for internal sites
                if (self._is_same_internal_site(parsed_url) and 
                    full_url.startswith(('http://', 'https://')) and
                    full_url not in self.visited_urls):
                    
                    clean_url = full_url.split('#')[0].split('?')[0].rstrip('/')
                    
                    if clean_url not in self.visited_urls and clean_url not in discovered_urls:
                        discovered_urls.append(clean_url)
            
            return discovered_urls
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to discover links from internal site {url}: {e}")
            return []
    
    def _is_same_internal_site(self, parsed_url) -> bool:
        """
        Check if URL belongs to the same internal site
        More flexible matching for internal development sites
        """
        base_parsed = urlparse(self.base_url)
        
        # Same hostname and port
        if parsed_url.netloc == base_parsed.netloc:
            return True
        
        # Handle cases where port might be implicit vs explicit
        base_host = base_parsed.hostname
        base_port = base_parsed.port or (443 if base_parsed.scheme == 'https' else 80)
        
        url_host = parsed_url.hostname  
        url_port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
        
        return base_host == url_host and base_port == url_port

def scrape_internal_website(base_url: str, max_pages: int = 50) -> Dict[str, Any]:
    """
    Scrape an internal website with authentication support
    """
    scraper = InternalWebsiteScraper(base_url, max_pages=max_pages)
    return scraper.scrape_website()