from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.embeddings import get_embeddings_client
from src.config import settings
import os

os.makedirs(settings.PERSIST_DIR, exist_ok=True)

def build_or_load_faiss(text, metadata=None, session_id=None):
    """
    Build FAISS vector store for a specific session/file
    Each session gets its own vector store to prevent cross-contamination
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.MAX_CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )
    
    # Split text into chunks
    chunks = text_splitter.split_text(text)
    docs = [Document(page_content=chunk, metadata=metadata or {}) for chunk in chunks]
    
    # Get embeddings client
    embed = get_embeddings_client()
    
    # Create session-specific directory if session_id provided
    if session_id:
        session_dir = os.path.join(settings.PERSIST_DIR, f"session_{session_id}")
        os.makedirs(session_dir, exist_ok=True)
        
        # Always create fresh vector store for new session
        db = FAISS.from_documents(docs, embed)
        db.save_local(session_dir)
        return db
    else:
        # Legacy behavior - create fresh vector store each time
        db = FAISS.from_documents(docs, embed)
        return db

def create_fresh_vectorstore(text, metadata=None):
    """
    Always create a fresh vector store (no persistence)
    This ensures no cross-contamination between different PDFs
    """
    # Check if text is empty or None
    if not text or not text.strip():
        return None  # Return None instead of raising error
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.MAX_CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )
    
    chunks = text_splitter.split_text(text)
    
    # Check if chunks were created
    if not chunks:
        return None  # Return None instead of raising error
    
    docs = [Document(page_content=chunk, metadata=metadata or {}) for chunk in chunks]
    
    # Check if documents were created
    if not docs:
        return None  # Return None instead of raising error
    
    embed = get_embeddings_client()
    db = FAISS.from_documents(docs, embed)
    
    return db

def cleanup_session_data(session_id):
    """Clean up vector store data for a specific session"""
    if session_id:
        session_dir = os.path.join(settings.PERSIST_DIR, f"session_{session_id}")
        if os.path.exists(session_dir):
            import shutil
            shutil.rmtree(session_dir)
