import requests
from bs4 import BeautifulSoup
import os
import shutil
from urllib.parse import urljoin, urlparse
from markdownify import markdownify as md
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
from basil_search.src.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebsiteScraper:
    
    def __init__(self, base_url: str, output_dir: Optional[Path] = None, max_pages: int = 50):
        self.base_url = base_url.rstrip('/')
        self.output_dir = output_dir or Config.SCRAPED_PAGES_DIR
        self.max_pages = max_pages
        self.visited_urls = set()
        self.urls_to_visit = [base_url]
        
        parsed_url = urlparse(base_url)
        self.base_domain = parsed_url.netloc
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def html_to_markdown(self, html_content: str, url: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        unwanted_tags = ["script", "style", "meta", "link", "footer", "nav", 
                        "header", "form", "svg", "button", "img"]
        for tag in soup(unwanted_tags):
            tag.extract()
        main_content = (soup.find('main') or 
                       soup.find('div', class_='main-content') or 
                       soup.find('article') or 
                       soup.find('body'))
        
        if not main_content:
            main_content = soup.body
        
        markdown_content = md(
            str(main_content), 
            heading_style="ATX", 
            strip_links=False
        )
        
        title = soup.title.string if soup.title else os.path.basename(urlparse(url).path) or "No Title"
        final_content = f"# {title.strip()}\n\n"
        final_content += f"Bron: {url.strip()}\n\n"
        final_content += markdown_content
        
        return final_content.strip()
    
    def scrape_page(self, url: str) -> bool:
        try:
            response = requests.get(url, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            markdown_content = self.html_to_markdown(response.text, url)
            
            filename = self._generate_filename(url)
            filepath = self.output_dir / f"{filename}.md"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Scraped: {url} -> {filepath}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            return False
    
    def _generate_filename(self, url: str) -> str:
        parsed_url = urlparse(url)
        path_parts = [p for p in parsed_url.path.split('/') if p]
        filename_base = '_'.join(path_parts) if path_parts else "index"
        
        domain_prefix = parsed_url.netloc.replace('.', '_') + '_'
        return f"{domain_prefix}{filename_base}"
    
    def discover_links(self, url: str) -> List[str]:
        discovered_urls = []
        
        try:
            response = requests.get(url, timeout=Config.REQUEST_TIMEOUT)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                parsed_url = urlparse(full_url)
                
                if (parsed_url.netloc == self.base_domain and 
                    full_url.startswith(('http://', 'https://')) and
                    full_url not in self.visited_urls):
                    
                    clean_url = full_url.split('#')[0].split('?')[0].rstrip('/')
                    
                    if clean_url not in self.visited_urls and clean_url not in discovered_urls:
                        discovered_urls.append(clean_url)
            
            return discovered_urls
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to discover links from {url}: {e}")
            return []
    
    def scrape_website(self) -> Dict[str, Any]:
        logger.info(f"Starting website scrape: {self.base_url}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Max pages: {self.max_pages}")
        
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        scraped_count = 0
        failed_count = 0
        
        while self.urls_to_visit and scraped_count < self.max_pages:
            current_url = self.urls_to_visit.pop(0)
            
            current_url = current_url.rstrip('/')
            if current_url in self.visited_urls:
                continue
            
            logger.info(f"Scraping ({scraped_count + 1}/{self.max_pages}): {current_url}")
            
            if self.scrape_page(current_url):
                self.visited_urls.add(current_url)
                scraped_count += 1
                
                new_links = self.discover_links(current_url)
                self.urls_to_visit.extend(new_links)
                
            else:
                failed_count += 1
        
        results = {
            'scraped_pages': scraped_count,
            'failed_pages': failed_count,
            'total_discovered': len(self.visited_urls) + len(self.urls_to_visit),
            'output_directory': str(self.output_dir),
            'base_url': self.base_url
        }
        
        logger.info(f"Scraping completed: {results}")
        return results

def scrape_website(base_url: str, max_pages: int = 50) -> Dict[str, Any]:
    scraper = WebsiteScraper(base_url, max_pages=max_pages)
    return scraper.scrape_website()