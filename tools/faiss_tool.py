import os
import faiss
import numpy as np
import pickle
import logging
import glob
from google import genai
from google.genai import types
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LogicFlow.Memory")

# Initialize the Stable Client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

class LogicFlowEmbedder:
    """Custom embedder to ensure V1 Stable consistency."""
    def __init__(self, model="gemini-embedding-001"):
        self.model = model

    def embed_documents(self, texts):
        response = client.models.embed_content(
            model=self.model,
            contents=texts,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
        )
        return [np.array(emb.values, dtype="float32") for emb in response.embeddings]

    def embed_query(self, text):
        response = client.models.embed_content(
            model=self.model,
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
        )
        return np.array(response.embeddings[0].values, dtype="float32")

def ingest_code():
    """Recursively scans the workspace and creates a fresh FAISS index."""
    # 1. Recursive Scan: Find all code files in demo/ and src/
    extensions = ['*.py', '*.c', '*.cpp', '*.h', '*.js']
    code_files = []
    for ext in extensions:
        code_files.extend(glob.glob(f"demo/**/{ext}", recursive=True))
        code_files.extend(glob.glob(f"src/**/{ext}", recursive=True))

    if not code_files:
        logger.warning("No code files found to index!")
        return

    all_docs = []
    for file_path in code_files:
        try:
            loader = TextLoader(file_path)
            all_docs.extend(loader.load())
        except Exception as e:
            logger.error(f"Could not load {file_path}: {e}")

    # 2. Split into logical chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600, 
        chunk_overlap=100,
        separators=["\nclass ", "\ndef ", "\n\n", "\n", " "]
    )
    split_docs = splitter.split_documents(all_docs)
    
    # Store page_content and source metadata for better retrieval
    texts = [doc.page_content for doc in split_docs]
    sources = [doc.metadata.get('source', 'unknown') for doc in split_docs]
    
    # Combine content with source for the LLM to know WHERE the code came from
    meta_data = [f"File: {src}\n{txt}" for src, txt in zip(sources, texts)]

    embedder = LogicFlowEmbedder()
    
    try:
        logger.info(f"Indexing {len(code_files)} files into memory...")
        embeddings = embedder.embed_documents(texts)
        vectors = np.vstack(embeddings)
        
        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim) 
        faiss.normalize_L2(vectors)
        index.add(vectors)
        
        os.makedirs(Config.VECTORSTORE_PATH, exist_ok=True)
        index_file = os.path.join(Config.VECTORSTORE_PATH, "index.bin")
        meta_file = os.path.join(Config.VECTORSTORE_PATH, "meta.pkl")
        
        faiss.write_index(index, index_file)
        with open(meta_file, "wb") as f:
            pickle.dump(meta_data, f)
            
        logger.info(f"✅ Multi-File Memory stabilized with {len(meta_data)} chunks.")
    except Exception as e:
        logger.error(f"❌ Ingestion Failed: {e}")

def retrieve_context(query, k=5):
    """Retrieves relevant code snippets using the passed k value."""
    embedder = LogicFlowEmbedder()
    
    index_file = os.path.join(Config.VECTORSTORE_PATH, "index.bin")
    meta_file = os.path.join(Config.VECTORSTORE_PATH, "meta.pkl")
    
    if not os.path.exists(index_file):
        logger.error("FAISS index not found. Run ingestion first.")
        return []

    index = faiss.read_index(index_file)
    with open(meta_file, "rb") as f:
        meta_texts = pickle.load(f)

    # Embed the query
    query_vec = embedder.embed_query(query).reshape(1, -1)
    faiss.normalize_L2(query_vec)
    
    # CRITICAL FIX: Use the 'k' argument passed from core.py
    distances, indices = index.search(query_vec, k=k)
    
    # Return formatted snippets
    results = [meta_texts[i] for i in indices[0] if i != -1 and i < len(meta_texts)]
    return results