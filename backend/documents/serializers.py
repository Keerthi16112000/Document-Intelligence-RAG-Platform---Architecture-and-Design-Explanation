from rest_framework import serializers
from .models import Document, DocumentVersion, Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'celery_task_id', 'task_type', 'status', 'created_at', 'updated_at']

class DocumentVersionSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = DocumentVersion
        fields = ['id', 'version_number', 'file_name', 'file_type', 'file_size', 
                  'status', 'error_message', 'page_count', 'chunk_count', 'created_at', 'tasks']

class DocumentSerializer(serializers.ModelSerializer):
    versions = DocumentVersionSerializer(many=True, read_only=True)
    current_status = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'workspace', 'title', 'description', 'created_at', 'updated_at', 'uploaded_by', 'versions', 'current_status']
        read_only_fields = ['id', 'created_at', 'updated_at', 'uploaded_by']

    def get_current_status(self, obj):
        latest_version = obj.versions.order_by('-version_number').first()
        if latest_version:
            return latest_version.status
        return 'UNKNOWN'
