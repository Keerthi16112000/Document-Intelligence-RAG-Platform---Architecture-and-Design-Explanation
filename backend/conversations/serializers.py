from rest_framework import serializers
from .models import Conversation, Message, Citation

class CitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citation
        fields = ['id', 'document_chunk', 'relevance_score']

class MessageSerializer(serializers.ModelSerializer):
    citations = CitationSerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'created_at', 'citations']

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'workspace', 'title', 'created_at', 'updated_at', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at']
