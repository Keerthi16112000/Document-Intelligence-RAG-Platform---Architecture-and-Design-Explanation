import uuid
from django.db import models
from accounts.models import Workspace, User

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')

    def __str__(self):
        return self.title

class DocumentVersion(models.Model):
    STATUS_CHOICES = [
        ('UPLOADED', 'Uploaded'),
        ('PROCESSING', 'Processing'),
        ('READY', 'Ready'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField(default=1)
    
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50) # e.g., application/pdf
    file_size = models.BigIntegerField()
    storage_key = models.CharField(max_length=512)
    file_hash = models.CharField(max_length=64, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UPLOADED')
    error_message = models.TextField(blank=True, null=True)
    
    page_count = models.IntegerField(blank=True, null=True)
    chunk_count = models.IntegerField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.document.title} - v{self.version_number}"

class DocumentChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_version = models.ForeignKey(DocumentVersion, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.IntegerField()
    page_number = models.IntegerField(blank=True, null=True)
    text_content = models.TextField()
    
    # Vectors are stored in ChromaDB, mapped by this chunk's UUID.
    
    def __str__(self):
        return f"Chunk {self.chunk_index} of {self.document_version}"

class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    celery_task_id = models.CharField(max_length=255, unique=True)
    document_version = models.ForeignKey(DocumentVersion, on_delete=models.CASCADE, related_name='tasks')
    task_type = models.CharField(max_length=50) # e.g., 'ingestion'
    status = models.CharField(max_length=20, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
