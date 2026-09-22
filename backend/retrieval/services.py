from typing import List, Dict, Any, Tuple
from retrieval.chroma_client import get_chroma_client
from common.llm import get_llm_provider
from ingestion.tasks import get_embedding_model

def search_documents(query: str, workspace_id: str, document_id: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
    embedding_model = get_embedding_model()
    query_embedding = embedding_model.encode(query).tolist()
    
    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection(name="documents")
    
    where_clause = {"workspace_id": workspace_id}
    if document_id:
        where_clause["document_id"] = document_id
        
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_clause
    )
    
    chunks = []
    if results['ids'] and len(results['ids']) > 0:
        for i in range(len(results['ids'][0])):
            chunks.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results and results['distances'] else None
            })
            
    return chunks

def generate_rag_response(query: str, workspace_id: str, document_id: str = None) -> Tuple[str, List[Dict[str, Any]]]:
    # 1. Retrieve relevant chunks
    chunks = search_documents(query, workspace_id, document_id)
    
    # 2. Generate response using LLM
    llm_provider = get_llm_provider()
    response_text = llm_provider.generate_response(prompt=query, context_chunks=chunks)
    
    return response_text, chunks
