from django.contrib.auth import get_user_model
from django.test.utils import isolate_apps
from django.db import models, connection

from rest_framework.views import APIView

from Product.models import Product, Category
from generic.utils_test import APITransactionTestCase, APIRequestFactory, APIRequestTestCase
from generic.funcs import generate_state_full_jwt
from generic.classes import GenericHyperlinkedModelSerializer, IsAdminUserOrReadOnlyPermission

User = get_user_model()


class TestProduct(APITransactionTestCase):

    def setUp(self) -> None:
        self.user_fields = {
            'mobile_number': '09103791346',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir'
        }
        self.staff_user = User.objects.create_user(**self.user_fields, is_staff=True)
        self.state_full_token = generate_state_full_jwt(user=self.staff_user)
        self.product_data = {
            'name': 'new cake',
            'price': 254,
            'is_available': True,
        }

    def test_create_product(self):
        new_product = Product(**self.product_data)
        new_product.save(user=self.staff_user)

        self.assertTrue(Product.objects.filter(**self.product_data, updated_by=self.staff_user,
                                               created_by=self.staff_user).exists())

    def test_update_product_by_new_user(self):
        other_user_field = {
            'mobile_number': '09103791345',
            'first_name': 'ali',
            'last_name': 'Khosravi',
            'password': 'amir'
        }
        other_user = User.objects.create_user(**other_user_field)

        new_product = Product(**self.product_data)
        new_product.save(user=self.staff_user)
        product_to_update_in_db = Product.objects.filter(
            **self.product_data, updated_by=self.staff_user, created_by=self.staff_user
        ).get()

        product_to_update_in_db.save(user=other_user)

        self.assertTrue(Product.objects.filter(
            **self.product_data, updated_by=other_user, created_by=self.staff_user
        ).exists())


class TestCategory(APITransactionTestCase):

    def setUp(self) -> None:
        self.user_fields = {
            'mobile_number': '09103791346',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir'
        }
        self.staff_user = User.objects.create_user(**self.user_fields, is_staff=True)
        self.state_full_token = generate_state_full_jwt(user=self.staff_user)
        self.category_data = {
            'name': 'new cake',
        }

    def test_create_category(self):
        new_category = Category(**self.category_data)
        new_category.save(user=self.staff_user)

        self.assertTrue(Category.objects.filter(
            **self.category_data, updated_by=self.staff_user, created_by=self.staff_user).exists())

    def test_update_category_by_new_user(self):
        other_user_field = {
            'mobile_number': '09103791345',
            'first_name': 'ali',
            'last_name': 'Khosravi',
            'password': 'amir'
        }
        other_user = User.objects.create_user(**other_user_field)

        new_product = Category(**self.category_data)
        new_product.save(user=self.staff_user)
        category_to_update_in_db = Category.objects.filter(
            **self.category_data, updated_by=self.staff_user, created_by=self.staff_user
        ).get()

        category_to_update_in_db.save(user=other_user)

        self.assertTrue(Category.objects.filter(
            **self.category_data, updated_by=other_user, created_by=self.staff_user
        ).exists())
