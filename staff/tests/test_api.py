import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_anonymous_access_denied(api_client, structure):
    url = reverse('api-node-data')
    response = api_client.get(url, {'id': structure['root'].id})
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_authorized_access_success(api_client, user, structure):
    api_client.force_authenticate(user=user)
    url = reverse('api-node-data')

    response = api_client.get(url, {'id': structure['root'].id})
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert 'children' in data
    assert 'employees' in data

    assert len(data['children']) == 1
    assert data['children'][0]['name'] == "Child"
    assert len(data['employees']) == 1
    assert data['employees'][0]['full_name'] == "Worker"


@pytest.mark.django_db
def test_404_on_invalid_id(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse('api-node-data')
    response = api_client.get(url, {'id': 99999})
    assert response.status_code == 404
