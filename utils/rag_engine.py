import os, hashlib
from pypdf import PdfReader
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter

client = chromadb.PersistentClient(path="chroma_db")
ef = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_or_create_collection("notes", embedding_function=ef)
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

def ingest_pdf(pdf_path: str):
    doc_name = os.path.basename(pdf_path)
    ids, docs, metas = [], [], []
    for page_no, page in enumerate(PdfReader(pdf_path).pages, start=1):
        text = (page.extract_text() or "").strip()
        for i, chunk in enumerate(splitter.split_text(text) if text else []):
            ids.append(hashlib.sha1(f"{doc_name}|{page_no}|{i}|{chunk}".encode()).hexdigest())
            docs.append(chunk)
            metas.append({"source": doc_name, "page": page_no})
    if not docs:
        return False, "No text found in PDF."
    collection.upsert(ids=ids, documents=docs, metadatas=metas)
    return True, f"Ingested {len(docs)} chunks from {doc_name}."

def retrieve(query: str, top_k: int = 4):
    r = collection.query(query_texts=[query], n_results=top_k)
    return [
        {"id": i, "text": d, "source": m["source"], "page": m["page"], "distance": dist}
        for i, d, m, dist in zip(r["ids"][0], r["documents"][0], r["metadatas"][0], r["distances"][0])
    ]

def retrieve_context(query, top_k=4):
    chunks = retrieve(query, top_k)
    return "\n---\n".join(c["text"] for c in chunks)

def clear_db():
    global collection
    client.delete_collection("notes")
    collection = client.get_or_create_collection("notes", embedding_function=ef)