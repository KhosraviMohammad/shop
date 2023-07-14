from django.contrib.auth import get_user_model
from rest_framework import serializers

from generic.utils_test import APIViewTestCase, APIRequestTestCase

from generic.funcs import generate_state_full_jwt
from BaseUser.models import OutstandingAccessToken, BlackListedAccessToken

from BaseUser.serializers import UserRegisterSerializer, TokenObtainSerializer, BlockAccessTokenSerializer, \
    CustomTokenObtainPairSerializer

User = get_user_model()


#
class TestUserRegisterSerializer(APIRequestTestCase):
    view_name = 'rest-registration:register'

    def setUp(self) -> None:
        self.user_fields = {
            'mobile_number': '09103791346',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir',
            'gender': 'male',
        }

    def test_user_create(self):
        request = self.request_post(data=self.user_fields)
        user_register_serializer = UserRegisterSerializer(data=request.POST, context={'request': request})
        user_register_serializer.is_valid()
        user_register_serializer.save()

        user_in_db = User.objects.get(mobile_number='09103791346')
        self.assertEqual(user_in_db.username, self.user_fields.get('mobile_number'))
        self.assertEqual(user_in_db.first_name, self.user_fields.get('first_name'))
        self.assertEqual(user_in_db.last_name, self.user_fields.get('last_name'))
        self.assertEqual(user_in_db.gender, self.user_fields.get('gender'))
        self.assertTrue(user_in_db.check_password(self.user_fields.get('password')))


class TestCustomTokenObtainPairSerializer(APIRequestTestCase):
    view_name = 'token_obtain_pair'

    def setUp(self) -> None:
        self.user_fields = {
            'mobile_number': '09103791346',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir',
            'gender': 'male',
        }
        self.user = User.objects.create_user(**self.user_fields)

    def test_user_toke_is_stored_in_db(self):
        request = self.request_post(
            data={'mobile_number': self.user_fields.get('mobile_number'), 'password': self.user_fields.get('password'),
                  'encoding': 'utf-8'})
        user_register_serializer = CustomTokenObtainPairSerializer(data=request.POST, context={'request': request})
        user_register_serializer.is_valid()
        validated_data = user_register_serializer.validated_data
        self.assertIn('access', validated_data)
        self.assertIn('refresh', validated_data)
        self.assertTrue(OutstandingAccessToken.objects.filter(token=validated_data.get('access')).exists())


class TestBlockAccessTokenSerializer(APIRequestTestCase):
    view_name = 'access_token_blacklist'

    def setUp(self) -> None:
        self.user_fields = {
            'mobile_number': '09103791346',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir',
            'gender': 'male',
        }
        self.user = User.objects.create_user(**self.user_fields)
        self.state_full_token = generate_state_full_jwt(user=self.user)

    def test_access_token_is_in_black_list(self):
        request = self.request_post(data={'access': self.state_full_token.get('access')})
        block_access_token_serializer = BlockAccessTokenSerializer(data=request.POST, context={'request': request})
        block_access_token_serializer.is_valid()
        self.assertTrue(BlackListedAccessToken.objects.filter(token=self.state_full_token.get('access')).exists())

    def test_invalid_access_token_not_to_block(self):
        request = self.request_post(data={'access': self.state_full_token.get('refresh')})
        block_access_token_serializer = BlockAccessTokenSerializer(data=request.POST, context={'request': request})
        self.assertRaises(serializers.ValidationError, block_access_token_serializer.is_valid, raise_exception=True)

        request = self.request_post(data={'access': 'saadsssdfmjsdifjwuojefwioqajcmas'})
        block_access_token_serializer = BlockAccessTokenSerializer(data=request.POST, context={'request': request})
        self.assertRaises(serializers.ValidationError, block_access_token_serializer.is_valid, raise_exception=True)

    def test_not_to_authenticate_user_with_blocked_token(self):
        BlackListedAccessToken.objects.create(user=self.user, token=self.state_full_token.get('access'))
        request = self.request_post(data={'access': self.state_full_token.get('access')})
        block_access_token_serializer = BlockAccessTokenSerializer(data=request.POST, context={'request': request})
        self.assertRaises(serializers.ValidationError, block_access_token_serializer.is_valid, raise_exception=True)
