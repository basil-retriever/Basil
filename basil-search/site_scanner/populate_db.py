import os
import chromadb
from sentence_transformers import SentenceTransformer
import json
import markdown
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re  # Nodig voor het parsen van de intentie MD

# --- ChromaDB en Embedding Model Setup ---
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

# Zorg dat dit hetzelfde model is als in app.py
embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mini-lm-l12-v2')

# Collecties: één voor website content en één voor intentievoorbeelden
# De collecties worden hier opgehaald of aangemaakt als ze niet bestaan.
website_content_collection = client.get_or_create_collection(name="website_content_collection")
intent_examples_collection = client.get_or_create_collection(name="intent_examples_collection")


# --- HULPFUNCTIES VOOR CONTENT INGESTIE ---

def extract_text_from_json(filepath):
    """Leest een JSON-bestand en extraheert tekst."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Pas dit aan aan de structuur van jouw JSON-bestanden.
    # Dit is een voorbeeld:
    text_content = data.get('title', '') + "\n" + data.get('description', '') + "\n" + data.get('details', '')
    source_url = data.get('url', '')  # Of genereer op basis van bestandsnaam
    return text_content.strip(), source_url


def extract_text_from_md_file(filepath):
    """
    Leest een Markdown-bestand (van de scanner), extraheert platte tekst en bron-URL.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Gebruik markdown en BeautifulSoup om MD naar platte tekst te converteren
    html = markdown.markdown(md_content)
    plain_text = BeautifulSoup(html, "html.parser").get_text(separator='\n', strip=True)

    # Probeer de bron-URL te extraheren uit de 'Bron:' regel
    source_url_line = next((line for line in md_content.splitlines() if line.startswith('Bron: ')), None)
    if source_url_line:
        source_url = source_url_line.replace('Bron: ', '').strip()
    else:
        # Fallback: genereer URL op basis van pad/bestandsnaam.
        # BELANGRIJK: Pas 'base_url_for_files' aan naar je site's domein!
        base_url_for_files = "https://www.jouw-event-site.nl/"
        file_name_no_ext = os.path.basename(filepath).split('.')[0]
        # Verwijder de domein-prefix die door de scanner wordt toegevoegd
        if '_' in file_name_no_ext:
            file_name_no_ext = '_'.join(file_name_no_ext.split('_')[1:])

        page_slug = file_name_no_ext.replace('_', '/')
        if page_slug == "index":
            source_url = base_url_for_files
        else:
            source_url = urljoin(base_url_for_files, page_slug)

    return plain_text, source_url


def index_local_content(content_dir):
    """
    Scant de opgegeven content-map (inclusief gescrapte_pages) en indexeert content
    in de 'website_content_collection'.
    """
    print(f"Start met het indexeren van website content vanuit '{content_dir}'...")

    ids = []
    documents = []
    metadatas = []

    # Loop door alle bestanden in de content directory en submappen
    for root, _, files in os.walk(content_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            text_content = ""
            source_url = ""

            if filename.endswith(".json"):
                text_content, source_url = extract_text_from_json(filepath)
            elif filename.endswith(".md") and "intents.md" not in filename:  # Sla intents.md over
                text_content, source_url = extract_text_from_md_file(filepath)

            if text_content:
                # Hier kun je de tekst nog chunking als deze erg lang is.
                # Voor nu, voegen we de hele pagina als één document toe.
                # Voor grote sites is chunking essentieel voor RAG-kwaliteit.
                # Voorbeeld van simpele chunking:
                # chunks = [text_content[i:i+500] for i in range(0, len(text_content), 500)]
                # for i, chunk in enumerate(chunks):
                #     doc_id = f"{os.path.basename(filepath)}_{i}"
                #     ids.append(doc_id)
                #     documents.append(chunk)
                #     metadatas.append({"source_url": source_url, "file_name": filename, "chunk_index": i})

                # Zonder chunking:
                doc_id = f"{os.path.basename(filepath)}_{len(ids)}"  # Unieke ID
                ids.append(doc_id)
                documents.append(text_content)
                metadatas.append({"source_url": source_url, "file_name": filename})

    if documents:
        print(f"Genereren van {len(documents)} embeddings voor website content en toevoegen aan ChromaDB...")
        # Leeg de collectie voor een schone start
        website_content_collection.delete(
            ids=[m['id'] for m in website_content_collection.peek(website_content_collection.count())['metadatas']])

        website_content_collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embedding_model.encode(documents).tolist()
        )
        print("Website content succesvol geïndexeerd in 'website_content_collection'.")
    else:
        print("Geen website content gevonden om te indexeren.")


# --- FUNCTIE VOOR INTENTIE VOORBEELDEN INGESTIE ---

def populate_intent_examples(intent_md_filepath):
    """
    Parset een Markdown-bestand met intentievoorbeelden en vult de intent_examples_collection in ChromaDB.
    """
    print(f"Start met het vullen van intentievoorbeelden vanuit '{intent_md_filepath}'...")

    if not os.path.exists(intent_md_filepath):
        print(f"Fout: Intentiebestand '{intent_md_filepath}' niet gevonden.")
        return

    ids = []
    documents = []
    metadatas = []
    current_intent = None
    doc_counter = 0

    with open(intent_md_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = re.split(r'# Intent: (.+)', content)

    for i in range(1, len(sections), 2):
        intent = sections[i].strip()
        lines = sections[i + 1].strip().split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('- ') and len(line) > 2:
                example_text = line[2:].strip()
                if example_text:
                    doc_id = f"{intent}_{doc_counter}"
                    ids.append(doc_id)
                    documents.append(example_text)
                    metadatas.append({"intent": intent})
                    doc_counter += 1

    if documents:
        print(f"Genereren van {len(documents)} embeddings voor intenties en toevoegen aan ChromaDB...")
        # Leeg de collectie voor een schone start
        intent_examples_collection.delete(
            ids=[m['id'] for m in intent_examples_collection.peek(intent_examples_collection.count())['metadatas']])

        intent_examples_collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embedding_model.encode(documents).tolist()
        )
        print("Intentievoorbeelden succesvol geïndexeerd in 'intent_examples_collection'.")
    else:
        print("Geen intentievoorbeelden gevonden om te indexeren.")


# --- HOOFD UITVOERBLOK ---
if __name__ == "__main__":
    # Zorg dat BeautifulSoup en Markdown geïnstalleerd zijn
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("Install BeautifulSoup for Markdown text extraction: pip install beautifulsoup4")
        exit("Required dependency missing.")
    try:
        import markdown
    except ImportError:
        print("Install markdown for Markdown parsing: pip install markdown")
        exit("Required dependency missing.")

    # BELANGRIJK: Pas deze paden aan. Ze zijn relatief ten opzichte van waar populate_db.py draait.
    # Als populate_db.py in /monorepo-root/backend/ staat, en content in /monorepo-root/content/, dan:
    INTENT_MD_FILEPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'content', 'intents.md'))
    WEBSITE_CONTENT_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'content'))

    # Stap 1: Vul de intentievoorbeelden
    populate_intent_examples(INTENT_MD_FILEPATH)

    # Stap 2: Vul de website content (van de scanner of je eigen JSON/MD files)
    index_local_content(WEBSITE_CONTENT_BASE_DIR)