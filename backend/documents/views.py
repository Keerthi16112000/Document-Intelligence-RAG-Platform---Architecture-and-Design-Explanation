from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Document, DocumentVersion, Task
from accounts.models import Workspace
from .serializers import DocumentSerializer, DocumentVersionSerializer, TaskSerializer
from common.storage import get_storage_client
from ingestion.tasks import process_document

class DocumentListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        workspace_id = self.request.query_params.get('workspace')
        if not workspace_id:
            return Document.objects.none()
        
        # Check if user has access to workspace
        workspace = Workspace.objects.filter(id=workspace_id).first()
        if not workspace or (workspace.owner != self.request.user and self.request.user not in workspace.members.all()):
            return Document.objects.none()
            
        return Document.objects.filter(workspace_id=workspace_id)

    def create(self, request, *args, **kwargs):
        workspace_id = request.data.get('workspace')
        file_obj = request.FILES.get('file')
        title = request.data.get('title')
        description = request.data.get('description', '')

        if not workspace_id or not file_obj or not title:
            return Response({'error': 'workspace, file, and title are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate workspace access
        try:
            workspace = Workspace.objects.get(id=workspace_id)
            if workspace.owner != request.user and request.user not in workspace.members.all():
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        except Workspace.DoesNotExist:
            return Response({'error': 'Workspace not found'}, status=status.HTTP_404_NOT_FOUND)

        # 1. Create Document
        document = Document.objects.create(
            workspace=workspace,
            title=title,
            description=description,
            uploaded_by=request.user
        )

        # 2. Save file via storage abstraction
        storage = get_storage_client()
        storage_key = storage.save(file_obj, file_obj.name)

        # 3. Create DocumentVersion
        doc_version = DocumentVersion.objects.create(
            document=document,
            version_number=1,
            file_name=file_obj.name,
            file_type=file_obj.content_type,
            file_size=file_obj.size,
            storage_key=storage_key,
            status='UPLOADED'
        )

        # 4. Create Task record
        task = Task.objects.create(
            document_version=doc_version,
            task_type='ingestion',
            status='PENDING',
            celery_task_id='pending'
        )

        # 5. Queue Celery task
        celery_result = process_document.delay(str(task.id))
        task.celery_task_id = celery_result.id
        task.save()

        serializer = self.get_serializer(document)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class DocumentDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DocumentSerializer

    def get_queryset(self):
        # We'll rely on object level permissions if needed, but for now just filter by workspaces user has access to
        workspaces = Workspace.objects.filter(owner=self.request.user) | self.request.user.workspaces.all()
        return Document.objects.filter(workspace__in=workspaces)

class TaskStatusView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TaskSerializer

    def get_queryset(self):
        workspaces = Workspace.objects.filter(owner=self.request.user) | self.request.user.workspaces.all()
        return Task.objects.filter(document_version__document__workspace__in=workspaces)
