from io import BytesIO

from django.contrib.auth import get_user_model
from rest_framework import serializers

from Product.models import Product
from generic.utils_test import APITransactionTestCase, APIRequestFactory

from generic.funcs import generate_state_full_jwt
from BaseUser.models import OutstandingAccessToken, BlackListedAccessToken

from Product.serializers import ProductSerializer

User = get_user_model()


class TestProductSerializer(APITransactionTestCase):

    def setUp(self) -> None:
        self.user_fields = {
            'mobile_number': '09103791346',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir'
        }
        self.user = User.objects.create_user(**self.user_fields)
        self.state_full_token = generate_state_full_jwt(user=self.user)
        self.request = APIRequestFactory()
        with open('/home/ubunto/Public/programming/python/django/tests/shop/Product/test/img.png') as image_file:
            image_file_data = image_file.buffer.read()
            image_file = BytesIO(image_file_data)
            image_file.name = 'new_cake.png'
            self.product_data = {
                'name': 'cake',
                'price': 254,
                'image': image_file,
                'is_available': True,
            }

    def test_create_product(self):
        request = self.request.post('', data=self.product_data)
        request.user = self.user
        product_serializer = ProductSerializer(data=request.POST, context={'request': request})
        product_serializer.is_valid()
        product_serializer.save()

        self.assertTrue(Product.objects.filter(
            name=self.product_data.get('name'),
            price=self.product_data.get('price'),
            is_available=self.product_data.get('is_available'),
            created_by=self.user,
            updated_by=self.user
        ).exists())

    def test_update_product_with_new_user(self):
        product_obj = Product.objects.create(
            name='A13', price=56, is_available=False, created_by=self.user, updated_by=self.user
        )
        new_user = User.objects.create_user(
            mobile_number='09103791345', first_name='ali', last_name='hasan', password='amir',
        )
        request = self.request.post('', data=self.product_data)
        request.user = new_user
        product_serializer = ProductSerializer(instance=product_obj, data=request.POST, context={'request': request})
        product_serializer.is_valid()
        product_serializer.save()
        self.assertTrue(Product.objects.filter(
            name=self.product_data.get('name'),
            price=self.product_data.get('price'),
            is_available=self.product_data.get('is_available'),
            created_by=self.user,
            updated_by=new_user
        ).exists())

# class TestCustomTokenObtainPairSerializer(APIRequestTestCase):
#     view_name = 'token_obtain_pair'
#
#     def setUp(self) -> None:
#         self.user_fields = {
#             'mobile_number': '09103791346',
#             'first_name': 'Mohammad',
#             'last_name': 'Khosravi',
#             'password': 'amir',
#             'gender': 'male',
#         }
#         self.user = User.objects.create_user(**self.user_fields)
#
#     def test_user_toke_is_stored_in_db(self):
#         request = self.request_post(
#             data={'mobile_number': self.user_fields.get('mobile_number'), 'password': self.user_fields.get('password'),
#                   'encoding': 'utf-8'})
#         user_register_serializer = CustomTokenObtainPairSerializer(data=request.POST, context={'request': request})
#         user_register_serializer.is_valid()
#         validated_data = user_register_serializer.validated_data
#         self.assertIn('access', validated_data)
#         self.assertIn('refresh', validated_data)
#         self.assertTrue(OutstandingAccessToken.objects.filter(token=validated_data.get('access')).exists())


# class TestBlockAccessTokenSerializer(APIRequestTestCase):
#     view_name = 'access_token_blacklist'
#
#     def setUp(self) -> None:
#         self.user_fields = {
#             'mobile_number': '09103791346',
#             'first_name': 'Mohammad',
#             'last_name': 'Khosravi',
#             'password': 'amir',
#             'gender': 'male',
#         }
#         self.user = User.objects.create_user(**self.user_fields)
#         self.state_full_token = generate_state_full_jwt(user=self.user)
#
#     def test_access_token_is_in_black_list(self):
#         request = self.request_post(data={'access': self.state_full_token.get('access')})
#         block_access_token_serializer = BlockAccessTokenSerializer(data=request.POST, context={'request': request})
#         block_access_token_serializer.is_valid()
#         self.assertTrue(BlackListedAccessToken.objects.filter(token=self.state_full_token.get('access')).exists())
#
#     def test_invalid_access_token_not_to_block(self):
#         request = self.request_post(data={'access': self.state_full_token.get('refresh')})
#         block_access_token_serializer = BlockAccessTokenSerializer(data=request.POST, context={'request': request})
#         self.assertRaises(serializers.ValidationError, block_access_token_serializer.is_valid, raise_exception=True)
#
#         request = self.request_post(data={'access': 'saadsssdfmjsdifjwuojefwioqajcmas'})
#         block_access_token_serializer = BlockAccessTokenSerializer(data=request.POST, context={'request': request})
#         self.assertRaises(serializers.ValidationError, block_access_token_serializer.is_valid, raise_exception=True)
#
#     def test_not_to_authenticate_user_with_blocked_token(self):
#         BlackListedAccessToken.objects.create(user=self.user, token=self.state_full_token.get('access'))
#         request = self.request_post(data={'access': self.state_full_token.get('access')})
#         block_access_token_serializer = BlockAccessTokenSerializer(data=request.POST, context={'request': request})
#         self.assertRaises(serializers.ValidationError, block_access_token_serializer.is_valid, raise_exception=True)
