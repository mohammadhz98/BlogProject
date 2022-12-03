from rest_framework import status
import pytest

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


    def test_if_user_is_not_admin_return_own_user_and_200(self, api_client, authenticate):
        authenticate()

        response = api_client.get('/api/v1/blog/users/')

        assert response.status_code == status.HTTP_200_OK
        #todo : check just own user data must get back
        # assert response.data['id'] > 0

