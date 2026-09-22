from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserDetailView, WorkspaceListCreateView, WorkspaceDetailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserDetailView.as_view(), name='user_detail'),
    path('workspaces/', WorkspaceListCreateView.as_view(), name='workspace_list'),
    path('workspaces/<uuid:pk>/', WorkspaceDetailView.as_view(), name='workspace_detail'),
]
