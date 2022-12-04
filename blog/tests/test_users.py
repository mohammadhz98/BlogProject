from django.contrib.auth import get_user_model
from rest_framework import status
import pytest
from model_bakery import baker

from rest_framework.test import APIClient

@pytest.fixture
def user_dict():
    return {
            "username" : "a",
            "password" : "a", 
            "email" : "a@a.com"
        }


@pytest.mark.django_db
class TestCreateUser():
    
    def test_if_data_is_valid_return_201(self, api_client, user_dict):
        response = api_client.post('/api/v1/blog/users/', user_dict)

        assert response.status_code == status.HTTP_201_CREATED


    def test_if_data_is_invalid_return_400(self, api_client, user_dict):
        for key, value in user_dict.items():
            user_dict[key] = ''

            response = api_client.post('/api/v1/blog/users/', user_dict)

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            user_dict[key] = value


@pytest.mark.django_db
class TestListUser():

    def test_if_user_is_anonymous_return_401(self, api_client):
        response = api_client.get('/api/v1/blog/users/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_if_user_is_non_admin_return_current_user_and_200(self, api_client):
        baker.make(get_user_model(),is_staff=True)
        user_non_admin = baker.make(get_user_model())
        
        api_client.force_authenticate(user=user_non_admin)
        response = api_client.get('/api/v1/blog/users/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert user_non_admin.id in [response.data[0]['id']]


    def test_if_user_is_admin_return_all_user_and_200(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin = baker.make(get_user_model())
        
        api_client.force_authenticate(user=user_admin)
        response = api_client.get('/api/v1/blog/users/')
        print(response.data)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert user_admin.id in [response.data[0]['id'], response.data[1]['id']]
        assert user_non_admin.id in [response.data[0]['id'], response.data[1]['id']]


@pytest.mark.django_db
class TestRetrievetUser():

    def test_if_user_is_anonymous_return_401(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin = baker.make(get_user_model())

        response_admin = api_client.get(f'/api/v1/blog/users/{user_admin.id}/')
        response_non_admin = api_client.get(f'/api/v1/blog/users/{user_non_admin.id}/')

        assert response_admin.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_non_admin.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.skip
    def test_if_user_is_non_admin_return_current_user_and_200(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin = baker.make(get_user_model())

        api_client.force_authenticate(user=user_non_admin)

        response_admin = api_client.get(f'/api/v1/blog/users/{user_admin.id}/')
        response_non_admin = api_client.get(f'/api/v1/blog/users/{user_non_admin.id}/')

        assert response_admin.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_non_admin.status_code == status.HTTP_200_OK
        assert user_non_admin.id in [response_non_admin.data[0]['id']]



    def test_if_user_is_admin_return_all_user_and_200(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin = baker.make(get_user_model())

        api_client.force_authenticate(user=user_admin)

        response_admin = api_client.get(f'/api/v1/blog/users/{user_admin.id}/')
        response_non_admin = api_client.get(f'/api/v1/blog/users/{user_non_admin.id}/')

        assert response_admin.status_code == status.HTTP_200_OK
        assert user_admin.id in [response_admin.data['id']]
        assert response_non_admin.status_code == status.HTTP_200_OK
        assert user_non_admin.id in [response_non_admin.data['id']]



