from langchain_huggingface  import HuggingFaceEmbeddings
from src.config import settings

def get_embeddings_client():
    return HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
