# load_chroma_data.py
import os
import chromadb
from sentence_transformers import SentenceTransformer
import re


embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection_name = "ticket_intent_collection"

try:
    collection = chroma_client.get_collection(name=collection_name)
    print(f"Collection '{collection_name}' already exists. Deleting and recreating for a fresh load.")
    chroma_client.delete_collection(name=collection_name)
except:
    print(f"Creating new collection '{collection_name}'.")
collection = chroma_client.create_collection(
    name=collection_name,
    embedding_function=None,
    metadata={"hnsw:space": "cosine"}
)

def parse_markdown_training_data(filepath):
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = re.split(r'# Intent: (.+)', content)

    for i in range(1, len(sections), 2):
        intent = sections[i].strip()
        lines = sections[i+1].strip().split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('- ') and len(line) > 2:
                text = line[2:].strip()
                data.append({"text": text, "intent": intent})
    return data

if __name__ == "__main__":
    markdown_filepath = "training_data_en.md"

    if not os.path.exists(markdown_filepath):
        print(f"error: '{markdown_filepath}' not found.")
        exit()

    print(f"load data from {markdown_filepath}...")
    training_examples = parse_markdown_training_data(markdown_filepath)

    if not training_examples:
        print("No examples found.")
        exit()

    print(f"found {len(training_examples)} examples.")

    texts = [example["text"] for example in training_examples]
    intents = [example["intent"] for example in training_examples]

    ids = [f"doc_{i}" for i in range(len(training_examples))]

    print("Generating emdeddings.. Might take while.")
    embeddings = embedding_model.encode(texts).tolist()

    print("Adding data to ChromaDb...")
    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=[{"intent": intent} for intent in intents],
        ids=ids
    )
    print("Data loaded into ChromaDB successfully.")
    print(f"amount of items: {collection.count()}")