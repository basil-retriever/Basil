import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from basil_search.src.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaManager:
    
    def __init__(self, db_path: Optional[Path] = None, collection_name: Optional[str] = None):
        self.db_path = db_path or Config.CHROMA_DB_DIR
        self.collection_name = collection_name or Config.CHROMA_COLLECTION_NAME
        
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"ChromaDB initialized: {self.db_path}")
    
    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to ChromaDB")
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {e}")
            raise
    
    def search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'document': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0,
                        'similarity': 1 - results['distances'][0][i] if results['distances'] else 1
                    })
            
            return {
                'query': query,
                'results': formatted_results,
                'total_results': len(formatted_results)
            }
            
        except Exception as e:
            logger.error(f"Error searching ChromaDB: {e}")
            raise
    
    def load_from_file(self, file_path: Path, source_type: str = "content") -> int:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            sections = content.split('## ')
            sections = [s.strip() for s in sections if s.strip()]
            
            documents = []
            metadatas = []
            ids = []
            
            for i, section in enumerate(sections):
                if len(section) > 50:
                    lines = section.split('\n')
                    title = lines[0].strip()
                    
                    source_url = "Unknown"
                    for line in lines:
                        if line.startswith("**Source:**"):
                            source_url = line.replace("**Source:**", "").strip()
                            break
                    
                    documents.append(section)
                    metadatas.append({
                        'title': title,
                        'source': source_url,
                        'source_type': source_type,
                        'file_path': str(file_path),
                        'section_index': i
                    })
                    ids.append(f"{source_type}_{file_path.stem}_{i}")
            
            if documents:
                self.add_documents(documents, metadatas, ids)
                logger.info(f"Loaded {len(documents)} sections from {file_path}")
            
            return len(documents)
            
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            return 0
    
    def load_processed_files(self) -> Dict[str, int]:
        output_paths = Config.get_output_paths()
        results = {}
        
        if output_paths['overview'].exists():
            results['overview'] = self.load_from_file(
                output_paths['overview'], 
                source_type="content"
            )
        else:
            logger.warning(f"Overview file not found: {output_paths['overview']}")
            results['overview'] = 0
        
        if output_paths['search_sentences'].exists():
            results['search_sentences'] = self.load_from_file(
                output_paths['search_sentences'], 
                source_type="sentences"
            )
        else:
            logger.warning(f"Search sentences file not found: {output_paths['search_sentences']}")
            results['search_sentences'] = 0
        
        total_loaded = results['overview'] + results['search_sentences']
        logger.info(f"Loaded {total_loaded} total documents into ChromaDB")
        
        return results
    
    def clear_collection(self) -> None:
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("ChromaDB collection cleared")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        try:
            count = self.collection.count()
            return {
                'document_count': count,
                'collection_name': self.collection_name,
                'db_path': str(self.db_path)
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {'document_count': 0, 'error': str(e)}

def setup_chromadb() -> ChromaManager:
    return ChromaManager()