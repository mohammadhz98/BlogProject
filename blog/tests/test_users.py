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
        assert user_non_admin.id == response.data[0]['id']

    def test_if_user_is_admin_return_all_user_and_200(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin = baker.make(get_user_model())
        
        api_client.force_authenticate(user=user_admin)
        response = api_client.get('/api/v1/blog/users/')

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
        response_invalid = api_client.get(f'/api/v1/blog/users/{10000000}/')

        assert response_admin.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_non_admin.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_invalid.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_non_admin_return_current_user_and_200(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin1 = baker.make(get_user_model())
        user_non_admin2 = baker.make(get_user_model())

        api_client.force_authenticate(user=user_non_admin1)

        response_admin = api_client.get(f'/api/v1/blog/users/{user_admin.id}/')
        response_non_admin1 = api_client.get(f'/api/v1/blog/users/{user_non_admin1.id}/')
        response_non_admin2 = api_client.get(f'/api/v1/blog/users/{user_non_admin2.id}/')
        response_invalid = api_client.get(f'/api/v1/blog/users/{10000000}/')


        assert response_admin.status_code == status.HTTP_404_NOT_FOUND
        assert response_invalid.status_code == status.HTTP_404_NOT_FOUND      
        assert response_non_admin2.status_code == status.HTTP_404_NOT_FOUND      
        assert response_non_admin1.status_code == status.HTTP_200_OK
        assert user_non_admin1.id == response_non_admin1.data['id']

    def test_if_user_is_admin_return_all_user_and_200(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin = baker.make(get_user_model())

        api_client.force_authenticate(user=user_admin)

        response_admin = api_client.get(f'/api/v1/blog/users/{user_admin.id}/')
        response_non_admin = api_client.get(f'/api/v1/blog/users/{user_non_admin.id}/')
        response_invalid = api_client.get(f'/api/v1/blog/users/{10000000}/')


        assert response_admin.status_code == status.HTTP_200_OK
        assert user_admin.id == response_admin.data['id']
        
        assert response_non_admin.status_code == status.HTTP_200_OK
        assert user_non_admin.id == response_non_admin.data['id']

        assert response_invalid.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestUpdateUser():
    def test_if_user_is_anonymous_return_401(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin = baker.make(get_user_model())
        data = {'username':'a', 'password':'a', 'eamil':'e@e.com'}

        response_admin = api_client.patch(f'/api/v1/blog/users/{user_admin.id}/', data)
        response_non_admin = api_client.patch(f'/api/v1/blog/users/{user_non_admin.id}/', data)
        response_invalid = api_client.patch(f'/api/v1/blog/users/{10000000}/', data)

        assert response_admin.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_non_admin.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_invalid.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_data_is_valid_and_user_is_non_admin_return_200(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin1 = baker.make(get_user_model())
        user_non_admin2 = baker.make(get_user_model())
        data = {'username':'a', 'password':'a', 'email':'e@e.com'}

        api_client.force_authenticate(user=user_non_admin1)

        response_admin = api_client.patch(f'/api/v1/blog/users/{user_admin.id}/', data)
        response_non_admin1 = api_client.patch(f'/api/v1/blog/users/{user_non_admin1.id}/', data)
        response_non_admin2 = api_client.patch(f'/api/v1/blog/users/{user_non_admin2.id}/', data)
        response_invalid = api_client.patch(f'/api/v1/blog/users/{10000000}/', data)


        assert response_admin.status_code == status.HTTP_404_NOT_FOUND
        assert response_invalid.status_code == status.HTTP_404_NOT_FOUND      
        assert response_non_admin2.status_code == status.HTTP_404_NOT_FOUND      
        assert response_non_admin1.status_code == status.HTTP_200_OK
        data.pop('password')
        for key, value in data.items():
            assert data[key] == response_non_admin1.data[key] == value

    def test_if_user_is_admin_return_all_user_and_200(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin = baker.make(get_user_model())

        api_client.force_authenticate(user=user_admin)

        data1 = {'username':'a', 'password':'a', 'email':'e@e.com'}
        response_admin = api_client.patch(f'/api/v1/blog/users/{user_admin.id}/', data1)

        data2 = {'username':'b', 'password':'b', 'email':'b@e.com'}
        response_non_admin = api_client.patch(f'/api/v1/blog/users/{user_non_admin.id}/', data2)

        data3 = {'username':'c', 'password':'c', 'email':'c@e.com'}
        response_invalid = api_client.patch(f'/api/v1/blog/users/{10000000}/', data3)


        assert response_admin.status_code == status.HTTP_200_OK
        data1.pop('password')
        for key, value in data1.items():
            assert data1[key] == response_admin.data[key] == value
        
        assert response_non_admin.status_code == status.HTTP_200_OK
        data2.pop('password')
        for key, value in data2.items():
            assert data2[key] == response_non_admin.data[key] == value

        assert response_invalid.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDeleteUser():
    def test_if_user_is_anonymous_return_401(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin = baker.make(get_user_model())

        response_admin = api_client.delete(f'/api/v1/blog/users/{user_admin.id}/')
        response_non_admin = api_client.delete(f'/api/v1/blog/users/{user_non_admin.id}/')
        response_invalid = api_client.delete(f'/api/v1/blog/users/{10000000}/')

        assert response_admin.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_non_admin.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_invalid.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_data_is_valid_and_user_is_non_admin_return_200(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin1 = baker.make(get_user_model())
        user_non_admin2 = baker.make(get_user_model())

        api_client.force_authenticate(user=user_non_admin1)

        response_admin = api_client.delete(f'/api/v1/blog/users/{user_admin.id}/')
        response_non_admin1 = api_client.delete(f'/api/v1/blog/users/{user_non_admin1.id}/')
        response_non_admin2 = api_client.delete(f'/api/v1/blog/users/{user_non_admin2.id}/')
        response_invalid = api_client.delete(f'/api/v1/blog/users/{10000000}/')


        assert response_admin.status_code == status.HTTP_404_NOT_FOUND
        assert response_invalid.status_code == status.HTTP_404_NOT_FOUND      
        assert response_non_admin2.status_code == status.HTTP_404_NOT_FOUND      
        assert response_non_admin1.status_code == status.HTTP_204_NO_CONTENT


    def test_if_user_is_admin_return_all_user_and_200(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin = baker.make(get_user_model())

        api_client.force_authenticate(user=user_admin)

        response_admin = api_client.delete(f'/api/v1/blog/users/{user_admin.id}/')
        response_non_admin = api_client.delete(f'/api/v1/blog/users/{user_non_admin.id}/')
        response_invalid = api_client.delete(f'/api/v1/blog/users/{10000000}/')

        assert response_admin.status_code == status.HTTP_204_NO_CONTENT
        assert response_non_admin.status_code == status.HTTP_204_NO_CONTENT
        assert response_invalid.status_code == status.HTTP_404_NOT_FOUND

