import pytest
from rest_framework.test import APIClient
from accounts.models import User, Workspace

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user():
    user = User.objects.create_user(username='testuser', password='password123', email='test@example.com')
    Workspace.objects.create(name="Default Workspace", owner=user)
    return user

@pytest.mark.django_db
def test_user_registration(api_client):
    response = api_client.post('/api/auth/register/', {
        'username': 'newuser',
        'password': 'newpassword123',
        'email': 'new@example.com'
    })
    assert response.status_code == 201
    assert 'access' in response.data
    assert 'refresh' in response.data
    
    # Check if default workspace was created
    user = User.objects.get(username='newuser')
    assert Workspace.objects.filter(owner=user).count() == 1

@pytest.mark.django_db
def test_login(api_client, test_user):
    response = api_client.post('/api/auth/login/', {
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access' in response.data

@pytest.mark.django_db
def test_get_workspaces(api_client, test_user):
    response = api_client.post('/api/auth/login/', {
        'username': 'testuser',
        'password': 'password123'
    })
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    
    response = api_client.get('/api/auth/workspaces/')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == "Default Workspace"
