from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Conversation, Message, Citation
from accounts.models import Workspace
from .serializers import ConversationSerializer, MessageSerializer
from retrieval.services import generate_rag_response

class ConversationListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ConversationSerializer

    def get_queryset(self):
        workspace_id = self.request.query_params.get('workspace')
        if not workspace_id:
            return Conversation.objects.none()
        
        workspace = Workspace.objects.filter(id=workspace_id).first()
        if not workspace or (workspace.owner != self.request.user and self.request.user not in workspace.members.all()):
            return Conversation.objects.none()
            
        return Conversation.objects.filter(workspace_id=workspace_id, created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ConversationDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(created_by=self.request.user)

class ChatMessageView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        try:
            conversation = Conversation.objects.get(id=pk, created_by=request.user)
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

        query = request.data.get('message')
        if not query:
            return Response({'error': 'message is required'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Save User Message
        user_msg = Message.objects.create(
            conversation=conversation,
            role='user',
            content=query
        )

        # 2. Generate RAG Response
        # We can optionally limit search to a specific document if provided in request
        document_id = request.data.get('document_id')
        response_text, chunks = generate_rag_response(
            query=query, 
            workspace_id=str(conversation.workspace.id),
            document_id=document_id
        )

        # 3. Save Assistant Message
        assistant_msg = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=response_text
        )

        # 4. Save Citations
        # In a robust implementation we'd link to actual DocumentChunk DB records, 
        # but for simplicity we store the metadata retrieved from ChromaDB
        for chunk in chunks:
            # We map ChromaDB chunk ID back to Postgres ID
            from documents.models import DocumentChunk
            try:
                db_chunk = DocumentChunk.objects.get(id=chunk['id'])
                Citation.objects.create(
                    message=assistant_msg,
                    document_chunk=db_chunk,
                    relevance_score=chunk['distance']
                )
            except DocumentChunk.DoesNotExist:
                pass

        if not conversation.title:
            conversation.title = query[:50] + "..."
            conversation.save()

        # Fetch full conversation to return
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)
