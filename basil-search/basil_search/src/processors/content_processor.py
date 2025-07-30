import glob
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from ..config import Config
from ..utils.groq_client import GroqClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentProcessor:
    
    def __init__(self, scraped_pages_dir: Optional[Path] = None):
        self.scraped_pages_dir = scraped_pages_dir or Config.SCRAPED_PAGES_DIR
        self.groq_client = GroqClient()
        
    def extract_page_content(self, file_path: Path) -> Optional[Dict[str, str]]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else "Untitled"
            
            url_match = re.search(r'^Bron: (.+)$', content, re.MULTILINE)
            url = url_match.group(1) if url_match else "Unknown URL"
            content_lines = content.split('\n')
            content_start = 0
            
            for i, line in enumerate(content_lines):
                if line.startswith('Bron:'):
                    content_start = i + 1
                    break
            
            main_content = '\n'.join(content_lines[content_start:]).strip()
            
            main_content = re.sub(r'\n{3,}', '\n\n', main_content)
            
            return {
                'title': title,
                'url': url,
                'content': main_content,
                'filename': file_path.name
            }
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return None
    
    def generate_search_sentences(self, page_data: Dict[str, str]) -> List[str]:
        if not Config.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not found. Skipping sentence generation.")
            return []
        
        prompt = f"""
Based on the following website content, generate 8-10 example sentences that users might search for or ask about when looking for this information.

Website Title: {page_data['title']}
Website URL: {page_data['url']}
Content: {page_data['content'][:1000]}...

Generate sentences in the format similar to these examples:
- "I need help with website development"
- "How much does a custom website cost?"
- "Where can I find web design services?"
- "I'm looking for a company that builds webshops"

Focus on natural language searches and questions that would lead users to this specific page. Make the sentences varied and cover different aspects of the content.

Return only the sentences, one per line, without numbers or bullet points.
"""
        
        try:
            response = self.groq_client.generate_text(prompt)
            
            sentences = []
            for line in response.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and len(line) > 10:
                    line = re.sub(r'^[-*•\d\.\)\s]+', '', line).strip()
                    if line:
                        sentences.append(line)
            
            logger.info(f"Generated {len(sentences)} sentences for: {page_data['filename']}")
            return sentences
            
        except Exception as e:
            logger.error(f"Error generating sentences for {page_data['filename']}: {e}")
            return []
    
    def consolidate_content(self, output_file: Path) -> int:
        md_files = list(self.scraped_pages_dir.glob("*.md"))
        
        if not md_files:
            logger.warning(f"No markdown files found in {self.scraped_pages_dir}")
            return 0
        
        consolidated_content = [
            "# Website Content Overview",
            "",
            "This file contains consolidated content from all scraped pages for ChromaDB indexing.",
            f"Generated from {len(md_files)} pages.",
            "",
            "---",
            ""
        ]
        
        processed_count = 0
        
        for file_path in sorted(md_files):
            page_data = self.extract_page_content(file_path)
            if page_data:
                consolidated_content.extend([
                    f"## {page_data['title']}",
                    "",
                    f"**Source:** {page_data['url']}",
                    f"**File:** {page_data['filename']}",
                    "",
                    page_data['content'],
                    "",
                    "---",
                    ""
                ])
                processed_count += 1
                logger.info(f"Consolidated: {page_data['filename']}")
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(consolidated_content))
        
        logger.info(f"Consolidation complete: {processed_count} pages -> {output_file}")
        return processed_count
    
    def generate_search_sentences_file(self, output_file: Path) -> int:
        md_files = list(self.scraped_pages_dir.glob("*.md"))
        
        if not md_files:
            logger.warning(f"No markdown files found in {self.scraped_pages_dir}")
            return 0
        
        search_sentences = [
            "# Website Search Sentences",
            "",
            "This file contains AI-generated example sentences for better semantic search matching.",
            f"Generated from {len(md_files)} pages using Groq API.",
            "",
            "---",
            ""
        ]
        
        processed_count = 0
        
        for file_path in sorted(md_files):
            page_data = self.extract_page_content(file_path)
            if page_data:
                logger.info(f"Generating sentences for: {page_data['filename']}")
                
                sentences = self.generate_search_sentences(page_data)
                
                if sentences:
                    search_sentences.extend([
                        f"## {page_data['title']}",
                        "",
                        f"**Source:** {page_data['url']}",
                        f"**File:** {page_data['filename']}",
                        "",
                        "**Example search queries:**",
                        ""
                    ])
                    
                    for sentence in sentences:
                        search_sentences.append(f"- {sentence}")
                    
                    search_sentences.extend(["", "---", ""])
                    processed_count += 1
                
                time.sleep(Config.RATE_LIMIT_DELAY)
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(search_sentences))
        
        logger.info(f"Search sentences complete: {processed_count} pages -> {output_file}")
        return processed_count
    
    def process_all(self) -> Dict[str, Any]:
        logger.info("Starting content processing...")
        
        output_paths = Config.get_output_paths()
        
        logger.info("Step 1: Consolidating content...")
        consolidated_count = self.consolidate_content(output_paths['overview'])
        
        logger.info("Step 2: Generating search sentences...")
        sentences_count = self.generate_search_sentences_file(output_paths['search_sentences'])
        
        results = {
            'consolidated_pages': consolidated_count,
            'search_sentences_pages': sentences_count,
            'overview_file': str(output_paths['overview']),
            'search_sentences_file': str(output_paths['search_sentences'])
        }
        
        logger.info(f"Processing complete: {results}")
        return results

def process_scraped_content(scraped_pages_dir: Optional[Path] = None) -> Dict[str, Any]:
    processor = ContentProcessor(scraped_pages_dir)
    return processor.process_all()