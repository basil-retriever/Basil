#!/usr/bin/env python3
"""
Script to consolidate scraped pages into a single overview file for ChromaDB indexing.
This creates a structured format similar to training_data_en.md for better semantic search.
Also generates example sentences using Groq API for better search matching.
"""

import os
import glob
from pathlib import Path
import re
import requests
import json
import time

from dotenv import load_dotenv

load_dotenv()

def extract_page_content(file_path):
    """Extract title, URL, and content from a scraped page."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title (first line starting with #)
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else "Untitled"
        
        # Extract source URL
        url_match = re.search(r'^Bron: (.+)$', content, re.MULTILINE)
        url = url_match.group(1) if url_match else "Unknown URL"
        
        # Extract main content (everything after the source URL)
        content_lines = content.split('\n')
        content_start = 0
        
        # Find where the main content starts (after "Bron:" line)
        for i, line in enumerate(content_lines):
            if line.startswith('Bron:'):
                content_start = i + 1
                break
        
        main_content = '\n'.join(content_lines[content_start:]).strip()
        
        # Clean up the content - remove excessive whitespace
        main_content = re.sub(r'\n{3,}', '\n\n', main_content)
        
        return {
            'title': title,
            'url': url,
            'content': main_content,
            'filename': os.path.basename(file_path)
        }
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def generate_search_sentences(page_data):
    """Generate example search sentences using Groq API."""
    
    # Get API key from environment
    groq_api_key = os.getenv('GROQ_API_KEY')
    if not groq_api_key:
        print("Warning: GROQ_API_KEY not found in environment. Skipping sentence generation.")
        return []
    
    # Prepare the prompt for generating search sentences
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
        # Make API request to Groq
        headers = {
            'Authorization': f'Bearer {groq_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = requests.post('https://api.groq.com/openai/v1/chat/completions', 
                               headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            sentences_text = result["choices"][0]["message"]["content"]
            
            # Parse the sentences
            sentences = []
            for line in sentences_text.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and len(line) > 10:
                    # Remove leading dashes, numbers, or other formatting
                    line = re.sub(r'^[-*•\d\.\)\s]+', '', line).strip()
                    if line:
                        sentences.append(line)
            
            print(f"Generated {len(sentences)} sentences for: {page_data['filename']}")
            return sentences
        else:
            print(f"Error from Groq API: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"Error generating sentences for {page_data['filename']}: {e}")
        return []

def consolidate_pages(scraped_pages_dir, output_file):
    """Consolidate all scraped pages into a single overview file."""
    
    # Get all markdown files in the scraped_pages directory
    md_files = glob.glob(os.path.join(scraped_pages_dir, "*.md"))
    
    if not md_files:
        print(f"No markdown files found in {scraped_pages_dir}")
        return
    
    consolidated_content = []
    processed_count = 0
    
    # Add header
    consolidated_content.append("# Website Content Overview")
    consolidated_content.append("")
    consolidated_content.append("This file contains consolidated content from all scraped pages for ChromaDB indexing.")
    consolidated_content.append(f"Generated from {len(md_files)} pages.")
    consolidated_content.append("")
    consolidated_content.append("---")
    consolidated_content.append("")
    
    # Process each file
    for file_path in sorted(md_files):
        page_data = extract_page_content(file_path)
        if page_data:
            # Add page section
            consolidated_content.append(f"## {page_data['title']}")
            consolidated_content.append("")
            consolidated_content.append(f"**Source:** {page_data['url']}")
            consolidated_content.append(f"**File:** {page_data['filename']}")
            consolidated_content.append("")
            consolidated_content.append(page_data['content'])
            consolidated_content.append("")
            consolidated_content.append("---")
            consolidated_content.append("")
            
            processed_count += 1
            print(f"Processed: {page_data['filename']}")
    
    # Write consolidated file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(consolidated_content))
        
        print(f"\nConsolidation complete!")
        print(f"Processed {processed_count} pages")
        print(f"Output written to: {output_file}")
        
    except Exception as e:
        print(f"Error writing output file: {e}")

def generate_search_sentences_file(scraped_pages_dir, output_file):
    """Generate search sentences for all pages and save to a separate file."""
    
    # Get all markdown files in the scraped_pages directory
    md_files = glob.glob(os.path.join(scraped_pages_dir, "*.md"))
    
    if not md_files:
        print(f"No markdown files found in {scraped_pages_dir}")
        return
    
    search_sentences = []
    processed_count = 0
    
    # Add header
    search_sentences.append("# Website Search Sentences")
    search_sentences.append("")
    search_sentences.append("This file contains AI-generated example sentences for better semantic search matching.")
    search_sentences.append(f"Generated from {len(md_files)} pages using Groq API.")
    search_sentences.append("")
    search_sentences.append("---")
    search_sentences.append("")
    
    # Process each file
    for file_path in sorted(md_files):
        page_data = extract_page_content(file_path)
        if page_data:
            print(f"Generating sentences for: {page_data['filename']}")
            
            # Generate search sentences using Groq API
            sentences = generate_search_sentences(page_data)
            
            if sentences:
                # Add page section
                search_sentences.append(f"## {page_data['title']}")
                search_sentences.append("")
                search_sentences.append(f"**Source:** {page_data['url']}")
                search_sentences.append(f"**File:** {page_data['filename']}")
                search_sentences.append("")
                search_sentences.append("**Example search queries:**")
                search_sentences.append("")
                
                # Add each sentence
                for sentence in sentences:
                    search_sentences.append(f"- {sentence}")
                
                search_sentences.append("")
                search_sentences.append("---")
                search_sentences.append("")
                
                processed_count += 1
            
            # Add a small delay to avoid rate limiting
            time.sleep(1)
    
    # Write search sentences file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(search_sentences))
        
        print(f"\nSearch sentences generation complete!")
        print(f"Processed {processed_count} pages")
        print(f"Output written to: {output_file}")
        
    except Exception as e:
        print(f"Error writing search sentences file: {e}")

def main():
    """Main function to run the consolidation."""
    # Set up paths
    script_dir = Path(__file__).parent
    scraped_pages_dir = script_dir / "content" / "scraped_pages"
    overview_file = script_dir / "content" / "website_content_overview.md"
    search_sentences_file = script_dir / "content" / "search_sentences.md"
    
    # Ensure directories exist
    if not scraped_pages_dir.exists():
        print(f"Directory not found: {scraped_pages_dir}")
        return
    
    # Create output directory if it doesn't exist
    overview_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Consolidating pages from: {scraped_pages_dir}")
    print(f"Overview file: {overview_file}")
    print(f"Search sentences file: {search_sentences_file}")
    print("-" * 50)
    
    # Generate the consolidated overview file
    print("Step 1: Generating website content overview...")
    consolidate_pages(scraped_pages_dir, overview_file)
    
    print("\n" + "=" * 50)
    
    # Generate search sentences using Groq API
    print("Step 2: Generating search sentences using Groq API...")
    generate_search_sentences_file(scraped_pages_dir, search_sentences_file)
    
    print("\n" + "=" * 50)
    print("All files generated successfully!")
    print("Files created:")
    print(f"- {overview_file}")
    print(f"- {search_sentences_file}")
    print("\nBoth files can now be loaded into ChromaDB for semantic search.")

if __name__ == "__main__":
    main()