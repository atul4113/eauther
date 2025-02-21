from rest_framework.test import APIClient


class AuthorizationTestMixin(object):
    def get_token(self, client, user):
        """
        Get JWT token for user
        Args:
            client: APIClient for making request
            user: database User entity

        Returns:
            String which contains JWT token

        """
        client.force_authenticate(user)
        response_token = client.get('/api/v2/jwt/session_token')
        assert 'token' in response_token.data, response_token.data

        return response_token.data['token']

    def login_in_as(self, user=None):
        """
        Login as user
        Args:
            user: database User entity

        Returns:
            ApiClient with configured credentials

        """
        client = APIClient()

        if user is not None:
            token = self.get_token(client, user)
            client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(token))

        return client