from celery import shared_task
from django.conf import settings
from documents.models import DocumentVersion, DocumentChunk, Task
from common.storage import get_storage_client
import tempfile
import os
import uuid
import PyPDF2
import docx

# Simulated chroma client for now
# We will write the real Chroma DB integration in retrieval app
from retrieval.chroma_client import get_chroma_client
from sentence_transformers import SentenceTransformer

model = None

def get_embedding_model():
    global model
    if model is None:
        model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

def extract_text_from_pdf(file_path):
    text = ""
    num_pages = 0
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        num_pages = len(reader.pages)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
    return text, num_pages

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text, None

def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

@shared_task(bind=True)
def process_document(self, task_id_str):
    task = Task.objects.get(id=task_id_str)
    doc_version = task.document_version
    
    try:
        task.status = 'PROCESSING'
        task.celery_task_id = self.request.id
        task.save()
        
        doc_version.status = 'PROCESSING'
        doc_version.save()

        storage = get_storage_client()
        file_bytes = storage.read(doc_version.storage_key)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=doc_version.file_name) as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name

        try:
            text = ""
            num_pages = None
            if doc_version.file_type == 'application/pdf':
                text, num_pages = extract_text_from_pdf(temp_file_path)
            elif 'wordprocessingml' in doc_version.file_type or doc_version.file_type == 'application/msword':
                text, num_pages = extract_text_from_docx(temp_file_path)
            else:
                # Assume text
                with open(temp_file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

            if num_pages:
                doc_version.page_count = num_pages

            chunks = chunk_text(text)
            doc_version.chunk_count = len(chunks)
            doc_version.save()

            embedding_model = get_embedding_model()
            chroma_client = get_chroma_client()
            collection = chroma_client.get_or_create_collection(name="documents")

            for i, chunk_text_content in enumerate(chunks):
                chunk = DocumentChunk.objects.create(
                    document_version=doc_version,
                    chunk_index=i,
                    text_content=chunk_text_content
                )
                
                # Generate embedding
                embedding = embedding_model.encode(chunk_text_content).tolist()
                
                # Store in ChromaDB
                collection.add(
                    ids=[str(chunk.id)],
                    embeddings=[embedding],
                    documents=[chunk_text_content],
                    metadatas=[{
                        "workspace_id": str(doc_version.document.workspace.id),
                        "document_id": str(doc_version.document.id),
                        "version_id": str(doc_version.id),
                        "chunk_index": i
                    }]
                )

            doc_version.status = 'READY'
            doc_version.save()
            
            task.status = 'COMPLETED'
            task.save()
            
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    except Exception as e:
        doc_version.status = 'FAILED'
        doc_version.error_message = str(e)
        doc_version.save()
        
        task.status = 'FAILED'
        task.save()
        raise e
