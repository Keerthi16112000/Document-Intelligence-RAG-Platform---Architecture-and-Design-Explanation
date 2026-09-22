from django.urls import path
from .views import DocumentListCreateView, DocumentDetailView, TaskStatusView

urlpatterns = [
    path('', DocumentListCreateView.as_view(), name='document_list_create'),
    path('<uuid:pk>/', DocumentDetailView.as_view(), name='document_detail'),
    path('tasks/<uuid:pk>/', TaskStatusView.as_view(), name='task_status'),
]
