from django.contrib.auth import get_user_model
from rest_framework import status
import pytest
from model_bakery import baker
from rest_framework.test import APIClient


@pytest.fixture
@pytest.mark.django_db
def user_admin():
    return baker.make(get_user_model(),is_staff=True)


@pytest.fixture
@pytest.mark.django_db
def user_non_admin():
    return baker.make(get_user_model())


@pytest.mark.django_db
class TestCreateMember():
    
    def test_create_member_return_403(self, api_client, user_admin, user_non_admin):
        response_anonymous = api_client.post('/api/v1/blog/members/')
        assert response_anonymous.status_code == status.HTTP_401_UNAUTHORIZED
        
        api_client.force_authenticate(user=user_non_admin)
        response_non_admin = api_client.post('/api/v1/blog/members/')
        assert response_non_admin.status_code == status.HTTP_403_FORBIDDEN
        
        api_client.force_authenticate(user=user_admin)
        response_admin = api_client.post('/api/v1/blog/members/')        
        assert response_admin.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestListMember():

    def test_if_user_is_anonymous_return_401(self, api_client):
        response = api_client.get('/api/v1/blog/members/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_non_admin_return_current_member_and_200(self, api_client):
        baker.make(get_user_model(),is_staff=True)
        user_non_admin = baker.make(get_user_model())
        
        api_client.force_authenticate(user=user_non_admin)
        response = api_client.get('/api/v1/blog/members/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert user_non_admin.id == response.data[0]['user']['id']

    def test_if_user_is_admin_return_all_user_and_200(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin = baker.make(get_user_model())
        
        api_client.force_authenticate(user=user_admin)
        response = api_client.get('/api/v1/blog/members/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert user_admin.id in [response.data[0]['user']['id'], response.data[1]['user']['id']]
        assert user_non_admin.id in [response.data[0]['user']['id'], response.data[1]['user']['id']]


@pytest.mark.django_db
class TestRetrievetUser():

    def test_if_user_is_anonymous_return_401(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin = baker.make(get_user_model())

        response_admin = api_client.get(f'/api/v1/blog/members/{user_admin.member.id}/')
        response_non_admin = api_client.get(f'/api/v1/blog/members/{user_non_admin.member.id}/')
        response_invalid = api_client.get(f'/api/v1/blog/members/{10000000}/')

        assert response_admin.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_non_admin.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_invalid.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_non_admin_return_current_user_and_200(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin1 = baker.make(get_user_model())
        user_non_admin2 = baker.make(get_user_model())

        api_client.force_authenticate(user=user_non_admin1)

        response_admin = api_client.get(f'/api/v1/blog/members/{user_admin.member.id}/')
        response_non_admin1 = api_client.get(f'/api/v1/blog/members/{user_non_admin1.member.id}/')
        response_non_admin2 = api_client.get(f'/api/v1/blog/members/{user_non_admin2.member.id}/')
        response_invalid = api_client.get(f'/api/v1/blog/members/{10000000}/')


        assert response_admin.status_code == status.HTTP_404_NOT_FOUND
        assert response_invalid.status_code == status.HTTP_404_NOT_FOUND      
        assert response_non_admin2.status_code == status.HTTP_404_NOT_FOUND      
        assert response_non_admin1.status_code == status.HTTP_200_OK
        assert user_non_admin1.id == response_non_admin1.data['user']['id']

    def test_if_user_is_admin_return_all_user_and_200(self, api_client):
        baker.make(get_user_model(),is_staff=True)
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin = baker.make(get_user_model())

        api_client.force_authenticate(user=user_admin)

        response_admin = api_client.get(f'/api/v1/blog/members/{user_admin.member.id}/')
        response_non_admin = api_client.get(f'/api/v1/blog/members/{user_non_admin.member.id}/')
        response_invalid = api_client.get(f'/api/v1/blog/members/{10000000}/')


        assert response_admin.status_code == status.HTTP_200_OK
        assert user_admin.id == response_admin.data['user']['id']
        
        assert response_non_admin.status_code == status.HTTP_200_OK
        assert user_non_admin.id == response_non_admin.data['user']['id']

        assert response_invalid.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestUpdateUser():
    def test_if_user_is_anonymous_return_401(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin = baker.make(get_user_model())
        data = {'phone':'a', 'address':'a'}

        response_admin = api_client.patch(f'/api/v1/blog/members/{user_admin.member.id}/', data)
        response_non_admin = api_client.patch(f'/api/v1/blog/members/{user_non_admin.member.id}/', data)
        response_invalid = api_client.patch(f'/api/v1/blog/members/{10000000}/', data)

        assert response_admin.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_non_admin.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_invalid.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_data_is_valid_and_user_is_non_admin_return_200(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin1 = baker.make(get_user_model())
        user_non_admin2 = baker.make(get_user_model())
        data = {'phone':'a', 'address':'a'}

        api_client.force_authenticate(user=user_non_admin1)

        response_admin = api_client.patch(f'/api/v1/blog/members/{user_admin.member.id}/', data)
        response_non_admin1 = api_client.patch(f'/api/v1/blog/members/{user_non_admin1.member.id}/', data)
        response_non_admin2 = api_client.patch(f'/api/v1/blog/members/{user_non_admin2.member.id}/', data)
        response_invalid = api_client.patch(f'/api/v1/blog/members/{10000000}/', data)


        assert response_admin.status_code == status.HTTP_404_NOT_FOUND
        assert response_invalid.status_code == status.HTTP_404_NOT_FOUND      
        assert response_non_admin2.status_code == status.HTTP_404_NOT_FOUND      
        assert response_non_admin1.status_code == status.HTTP_200_OK
        for key, value in data.items():
            assert data[key] == response_non_admin1.data[key] == value

    def test_if_user_is_admin_return_all_user_and_200(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin = baker.make(get_user_model())

        api_client.force_authenticate(user=user_admin)

        data1 = {'phone':'a', 'address':'a'}
        response_admin = api_client.patch(f'/api/v1/blog/members/{user_admin.member.id}/', data1)

        data2 = {'phone':'b', 'address':'b'}
        response_non_admin = api_client.patch(f'/api/v1/blog/members/{user_non_admin.member.id}/', data2)

        data3 = {'phone':'c', 'address':'c'}
        response_invalid = api_client.patch(f'/api/v1/blog/members/{10000000}/', data3)


        assert response_admin.status_code == status.HTTP_200_OK
        for key, value in data1.items():
            assert data1[key] == response_admin.data[key] == value
        
        assert response_non_admin.status_code == status.HTTP_200_OK
        for key, value in data2.items():
            assert data2[key] == response_non_admin.data[key] == value

        assert response_invalid.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDeleteUser():
    def test_if_user_is_anonymous_return_401(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin = baker.make(get_user_model())

        response_admin = api_client.delete(f'/api/v1/blog/members/{user_admin.member.id}/')
        response_non_admin = api_client.delete(f'/api/v1/blog/members/{user_non_admin.member.id}/')
        response_invalid = api_client.delete(f'/api/v1/blog/members/{10000000}/')

        assert response_admin.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_non_admin.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_invalid.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_data_is_valid_and_user_is_non_admin_return_200(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin1 = baker.make(get_user_model())
        user_non_admin2 = baker.make(get_user_model())

        api_client.force_authenticate(user=user_non_admin1)

        response_admin = api_client.delete(f'/api/v1/blog/members/{user_admin.member.id}/')
        response_non_admin1 = api_client.delete(f'/api/v1/blog/members/{user_non_admin1.member.id}/')
        response_non_admin2 = api_client.delete(f'/api/v1/blog/members/{user_non_admin2.member.id}/')
        response_invalid = api_client.delete(f'/api/v1/blog/members/{10000000}/')


        assert response_admin.status_code == status.HTTP_404_NOT_FOUND
        assert response_invalid.status_code == status.HTTP_404_NOT_FOUND      
        assert response_non_admin2.status_code == status.HTTP_404_NOT_FOUND      
        assert response_non_admin1.status_code == status.HTTP_204_NO_CONTENT


    def test_if_user_is_admin_return_all_user_and_200(self, api_client):
        user_admin = baker.make(get_user_model(),is_staff=True)
        user_non_admin = baker.make(get_user_model())

        api_client.force_authenticate(user=user_admin)

        response_admin = api_client.delete(f'/api/v1/blog/members/{user_admin.member.id}/')
        response_non_admin = api_client.delete(f'/api/v1/blog/members/{user_non_admin.member.id}/')
        response_invalid = api_client.delete(f'/api/v1/blog/members/{10000000}/')

        assert response_admin.status_code == status.HTTP_204_NO_CONTENT
        assert response_non_admin.status_code == status.HTTP_204_NO_CONTENT
        assert response_invalid.status_code == status.HTTP_404_NOT_FOUND

