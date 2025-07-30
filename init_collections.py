#!/usr/bin/env python3
"""
Initialize ChromaDB collections required for Basil to run.
"""

import chromadb
from sentence_transformers import SentenceTransformer

def init_collections():
    """Initialize all required ChromaDB collections."""
    print("Initializing ChromaDB collections...")
    
    # Create client
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Initialize intent collection if it doesn't exist
    try:
        collection = client.get_collection('ticket_intent_collection')
        print("✅ ticket_intent_collection already exists")
    except:
        print("🔄 Creating ticket_intent_collection...")
        collection = client.create_collection('ticket_intent_collection')
        
        # Add some basic intent examples
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        examples = [
            {'text': 'I want to buy a ticket', 'intent': 'purchase_ticket'},
            {'text': 'How much does a ticket cost?', 'intent': 'price_inquiry'},
            {'text': 'What events are available?', 'intent': 'event_inquiry'},
            {'text': 'Cancel my ticket', 'intent': 'cancel_ticket'},
            {'text': 'Hello there', 'intent': 'greeting'},
        ]
        
        texts = [ex['text'] for ex in examples]
        embeddings = model.encode(texts).tolist()
        
        collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=[{'intent': ex['intent']} for ex in examples],
            ids=[f'intent_{i}' for i in range(len(examples))]
        )
        
        print(f"✅ Added {len(examples)} intent examples to collection")
    
    # Initialize website_content collection if it doesn't exist
    try:
        collection = client.get_collection('website_content')
        print("✅ website_content already exists")
    except:
        print("🔄 Creating website_content collection...")
        collection = client.create_collection('website_content')
        print("✅ website_content collection created")
    
    print("🎉 All collections initialized successfully!")

if __name__ == "__main__":
    init_collections()