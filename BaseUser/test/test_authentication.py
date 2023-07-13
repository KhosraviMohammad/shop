from generic.classes import APIRequestTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from django.contrib.auth import get_user_model

from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from BaseUser.models import OutstandingAccessToken, BlackListedAccessToken
from rest_framework_simplejwt.exceptions import InvalidToken
from BaseUser.authentication import CustomJWTAuthentication
from generic.funcs import generate_state_full_jwt

User = get_user_model()


class TestCustomJWTAuthentication(APIRequestTestCase):

    def setUp(self) -> None:
        self.user_fields = {
            'mobile_number': '09103791346',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir'
        }
        self.request = APIRequestFactory()
        self.user = User.objects.create_user(**self.user_fields)
        self.state_full_token = generate_state_full_jwt(user=self.user)
        self.custom_JWT_authentication_obj = CustomJWTAuthentication()

    def test_authenticate_user_with_token(self):
        self.request.post('', HTTP_AUTHORIZATION=f'Bearer {self.state_full_token.get("access")}')
        self.request.META = {'HTTP_AUTHORIZATION': f'Bearer {self.state_full_token.get("access")}'.encode()}
        user, token = self.custom_JWT_authentication_obj.authenticate(request=self.request)
        self.assertEqual(self.user.id, user.id)
        self.assertEqual(self.user.mobile_number, user.mobile_number)
        self.assertEqual(token.token.decode(), self.state_full_token.get('access'))

    def test_not_to_authenticate_user_with_invalid_token(self):
        self.request.post('', HTTP_AUTHORIZATION=f'Bearer {self.state_full_token.get("refresh")}')
        self.request.META = {'HTTP_AUTHORIZATION': f'Bearer {self.state_full_token.get("refresh")}'.encode()}
        self.assertRaises(InvalidToken, self.custom_JWT_authentication_obj.authenticate, request=self.request)

        self.request.post('', HTTP_AUTHORIZATION=f'Bearer dasdasdasdasda')
        self.request.META = {'HTTP_AUTHORIZATION': f'Bearer dasdasdasdasda'.encode()}
        self.assertRaises(InvalidToken, self.custom_JWT_authentication_obj.authenticate, request=self.request)

    def test_not_to_authenticate_user_with_blocked_token(self):
        BlackListedAccessToken.objects.create(user=self.user, token=self.state_full_token.get('access'))
        self.request.post('', HTTP_AUTHORIZATION=f'Bearer {self.state_full_token.get("access")}')
        self.request.META = {'HTTP_AUTHORIZATION': f'Bearer {self.state_full_token.get("access")}'.encode()}
        self.assertRaises(InvalidToken, self.custom_JWT_authentication_obj.authenticate, request=self.request)
