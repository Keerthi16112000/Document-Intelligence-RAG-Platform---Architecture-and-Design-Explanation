import os
import chromadb
from chromadb.config import Settings

_chroma_client = None

def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        host = os.environ.get('CHROMA_HOST', 'localhost')
        port = os.environ.get('CHROMA_PORT', '8000')
        
        # For local dev without docker, we can fallback to ephemeral or persistent local
        try:
            _chroma_client = chromadb.HttpClient(host=host, port=port)
            _chroma_client.heartbeat() # test connection
        except Exception:
            # Fallback to local persistent if HTTP client fails
            from django.conf import settings
            _chroma_client = chromadb.PersistentClient(path=str(settings.BASE_DIR / 'chroma_db'))
            
    return _chroma_client
