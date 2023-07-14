from generic.utils_test import TestCase

from django.contrib.auth import get_user_model

from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from BaseUser.models import OutstandingAccessToken, BlackListedAccessToken
from BaseUser.auth_token_managers import JWTAuthTokenManager
from generic.funcs import generate_state_full_jwt

User = get_user_model()


class TestJWTAuthTokenManager(TestCase):
    def setUp(self) -> None:
        self.user_fields = {
            'mobile_number': '09103791346',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir'
        }
        self.user = User.objects.create_user(**self.user_fields)
        self.JWT_authentication_obj = JWTAuthTokenManager()

    def test_revoke_token_blocks_all_tokens_of_access_and_refresh(self):
        access_token_list = []
        refresh_token_list = []
        num_to_generate = 5
        for num in range(num_to_generate):
            token = generate_state_full_jwt(self.user)
            access_token_list.append(token.get('access'))
            refresh_token_list.append(token.get('refresh'))

        self.JWT_authentication_obj.revoke_token(self.user)
        self.assertEqual(BlackListedAccessToken.objects.filter(token__in=access_token_list, user=self.user).count(),
                         num_to_generate)

        outstanding_token_qu = OutstandingToken.objects.filter(token__in=refresh_token_list, user=self.user)
        self.assertEqual(BlacklistedToken.objects.filter(token__in=outstanding_token_qu).count(), num_to_generate)

    def test_provide_token_to_generate_token(self):
        token = self.JWT_authentication_obj.provide_token(self.user)
        self.assertIn('access', token)
        self.assertIn('refresh', token)
        self.assertTrue(OutstandingToken.objects.filter(token=token.get('refresh'), user=self.user).exists())
        self.assertTrue(OutstandingAccessToken.objects.filter(token=token.get('access'), user=self.user).exists())
