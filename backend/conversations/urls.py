from django.urls import path
from .views import ConversationListCreateView, ConversationDetailView, ChatMessageView

urlpatterns = [
    path('', ConversationListCreateView.as_view(), name='conversation_list_create'),
    path('<uuid:pk>/', ConversationDetailView.as_view(), name='conversation_detail'),
    path('<uuid:pk>/messages/', ChatMessageView.as_view(), name='chat_message'),
]
