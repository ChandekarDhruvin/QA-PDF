import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY",None)
    MODEL_NAME = os.getenv("MODEL_NAME", None)
    PERSIST_DIR = os.getenv("PERSIST_DIR", "./data/faiss_index")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data/uploads")
    MAX_CHUNK_SIZE = int(os.getenv("MAX_CHUNK_SIZE", None))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", None))
    EMBEDDING_MODEL =os.getenv("EMBEDDING_MODEL",None)

settings = Settings()
