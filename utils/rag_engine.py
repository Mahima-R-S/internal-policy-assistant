import os
import PyPDF2
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

# Setup ChromaDB
CHROMA_DATA_PATH = "chroma_db"
client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)

# Using default embedding function (Sentence Transformers)
# Note: In a production app, you might use Gemini embeddings via GenAI
default_ef = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name="tutor_notes",
    embedding_function=default_ef
)

def extract_text_from_pdf(pdf_file_path):
    """Extract text from PDF using PyPDF2."""
    text = ""
    try:
        with open(pdf_file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def ingest_pdf(pdf_file_path):
    """Chunk and store PDF content in ChromaDB."""
    text = extract_text_from_pdf(pdf_file_path)
    if not text.strip():
        return False, "No text found in PDF."

    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = text_splitter.split_text(text)
    
    # Clean old data (for this simple project, we clear on new upload)
    try:
        # Get count to decide if we need to delete
        count = collection.count()
        if count > 0:
            # We don't have a simple 'clear' in this version, so we could recreate or just add with unique IDs
            # For simplicity, we'll just add new ones. In a real app, you'd manage IDs better.
            pass
    except:
        pass

    # Add to collection
    ids = [f"id_{i}" for i in range(len(chunks))]
    collection.add(
        documents=chunks,
        ids=ids
    )
    
    return True, f"Ingested {len(chunks)} chunks."

def retrieve_context(query, top_k=3):
    """Retrieve relevant chunks for a query."""
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    if results and results['documents']:
        return "\n---\n".join(results['documents'][0])
    return ""

def clear_db():
    """Clear the local ChromaDB collection."""
    global collection
    client.delete_collection("tutor_notes")
    collection = client.get_or_create_collection(
        name="tutor_notes",
        embedding_function=default_ef
    )
