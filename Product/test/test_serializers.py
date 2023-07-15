from io import BytesIO

from django.contrib.auth import get_user_model

from Product.models import Product, Category
from generic.utils_test import APITransactionTestCase, APIRequestFactory

from generic.funcs import generate_state_full_jwt


from Product.serializers import ProductSerializer, CategorySerializer

User = get_user_model()


class TestProductSerializer(APITransactionTestCase):
    reset_sequences = True

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

    def test_update_product_with_category(self):
        category = Category.objects.create(
            name='A13', created_by=self.user, updated_by=self.user
        )
        product_to_update = Product.objects.create(
            name='A13', price=56, is_available=False, created_by=self.user, updated_by=self.user
        )
        new_user = User.objects.create_user(
            mobile_number='09103791345', first_name='ali', last_name='hasan', password='amir',
        )
        self.product_data['categories'] = [
            f'http://127.0.0.1:8000/api/v1/product/category/{category.id}/',
        ]

        request = self.request.post('', data=self.product_data)
        request.user = new_user
        product_serializer = ProductSerializer(
            instance=product_to_update,
            data=request.POST,
            context={'request': request}
        )
        product_serializer.is_valid()
        product_serializer.save()
        self.assertTrue(Product.objects.filter(
            name=self.product_data.get('name'),
            price=self.product_data.get('price'),
            is_available=self.product_data.get('is_available'),
            created_by=self.user,
            updated_by=new_user
        ).exists())

    def test_update_product_by_new_user(self):
        product_to_update = Product.objects.create(
            name='A13', price=56, is_available=False, created_by=self.user, updated_by=self.user
        )
        new_user = User.objects.create_user(
            mobile_number='09103791345', first_name='ali', last_name='hasan', password='amir',
        )
        request = self.request.post('', data=self.product_data)
        request.user = new_user
        product_serializer = ProductSerializer(instance=product_to_update, data=request.POST,
                                               context={'request': request})
        product_serializer.is_valid()
        product_serializer.save()
        self.assertTrue(Product.objects.filter(
            name=self.product_data.get('name'),
            price=self.product_data.get('price'),
            is_available=self.product_data.get('is_available'),
            created_by=self.user,
            updated_by=new_user
        ).exists())


class TestCategorySerializer(APITransactionTestCase):
    reset_sequences = True

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
            self.category_data = {
                'name': 'cake',
            }

    def test_create_category(self):
        request = self.request.post('', data=self.category_data)
        request.user = self.user
        category_serializer = CategorySerializer(data=request.POST, context={'request': request})
        category_serializer.is_valid()
        category_serializer.save()

        self.assertTrue(Category.objects.filter(
            name=self.category_data.get('name'),
            created_by=self.user,
            updated_by=self.user
        ).exists())

    def test_update_category_by_new_user(self):
        category_to_update = Category.objects.create(
            name='phone', created_by=self.user, updated_by=self.user
        )
        new_user = User.objects.create_user(
            mobile_number='09103791345', first_name='ali', last_name='hasan', password='amir',
        )
        request = self.request.post('', data=self.category_data)
        request.user = new_user
        category_serializer = CategorySerializer(
            instance=category_to_update,
            data=request.POST,
            context={'request': request}
        )
        category_serializer.is_valid()
        category_serializer.save()

        self.assertTrue(Category.objects.filter(
            name=self.category_data.get('name'),
            created_by=self.user,
            updated_by=new_user
        ).exists())
