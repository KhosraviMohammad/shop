from django.contrib.auth import get_user_model
from rest_framework import serializers

from generic.classes import APIViewTestCase

from generic.funcs import generate_state_full_jwt
from BaseUser.models import OutstandingAccessToken, BlackListedAccessToken

User = get_user_model()


class TestAccessTokenBlockView(APIViewTestCase):
    view_name = 'access_token_blacklist'

    def setUp(self) -> None:
        self.user_fields = {
            'mobile_number': '09103791346',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir'
        }
        self.user = User.objects.create_user(**self.user_fields)
        self.state_full_token = generate_state_full_jwt(user=self.user)

    def test_black_access_token(self):
        response = self.view_post(data={'access': self.state_full_token.get('access')})
        self.assertTrue(BlackListedAccessToken.objects.filter(token=self.state_full_token.get('access')).exists())
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)

    def test_black_invalid_access_token(self):
        response = self.view_post(data={'access': self.state_full_token.get('refresh')})
        self.assertEqual(response.status_code, 400)
        self.assertRaises(serializers.ValidationError)

        response = self.view_post(data={'access': 'saadsssdfmjsdifjwuojefwioqajcmas'})
        self.assertEqual(response.status_code, 400)
        self.assertRaises(serializers.ValidationError)

        BlackListedAccessToken.objects.create(user=self.user, token=self.state_full_token.get('access'))
        response = self.view_post(data={'access': self.state_full_token.get('access')})
        self.assertEqual(response.status_code, 400)
        self.assertRaises(serializers.ValidationError)