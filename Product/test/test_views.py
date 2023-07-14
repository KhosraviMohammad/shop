from io import BytesIO

from django.contrib.auth import get_user_model

from generic.utils_test import APITransactionTestCase

from generic.funcs import generate_state_full_jwt
from Product.models import Product, Category

User = get_user_model()


class TestProductListView(APITransactionTestCase):
    view_name = 'product-list'
    reset_sequences = True


    def setUp(self) -> None:
        self.user_fields = {
            'mobile_number': '09103791346',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir'
        }
        self.staff_user = User.objects.create_user(**self.user_fields, is_staff=True)
        self.state_full_token = generate_state_full_jwt(user=self.staff_user)
        self.cake_category = Category(name='cake', )
        self.cake_category.save(user=self.staff_user)
        self.cake_category_product_list = [
            Product(name='simple cake', price=100, is_available=True),
            Product(name='chocolate cake', price=150, is_available=False),
            Product(name='vanilla cake', price=143, is_available=True),
        ]

        for product in self.cake_category_product_list:
            product.save(user=self.staff_user)
            product.categories.set([self.cake_category])
        self.other_product = [
            Product(name='other', price=250, is_available=True),
        ]

        self.other_product[0].save(user=self.staff_user)

    def test_get_product_list_view(self):
        response = self.view_get()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('count'), 4)
        self.assertIn('results', response.data)

        response = self.view_get(query_string=f'categories={self.cake_category.id}')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data.get('count'), Product.objects.filter(categories=self.cake_category).count())
        self.assertIn('results', response.data)

    def test_creat_product(self):
        with open('/home/ubunto/Public/programming/python/django/tests/shop/Product/test/img.png') as image_file:
            image_file_data = image_file.buffer.read()
            image_file = BytesIO(image_file_data)
            image_file.name = 'new_cake.png'
            product_data = {
                'name': 'new cake',
                'price': 254,
                'image': image_file,
                'is_available': True,
            }
            response = self.view_post(
                data=product_data,
                format='multipart',
                HTTP_AUTHORIZATION=f'Bearer {self.state_full_token.get("access")}'
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 5)

    def test_creat_product_with_category(self):
        new_category = Category.objects.create(name='new category')
        with open('/home/ubunto/Public/programming/python/django/tests/shop/Product/test/img.png') as image_file:
            image_file_data = image_file.buffer.read()
            image_file = BytesIO(image_file_data)
            image_file.name = 'new_cake.png'
            product_data = {
                'name': 'new cake',
                'price': 254,
                'image': image_file,
                'is_available': True,
                'categories': [
                    f'http://127.0.0.1:8000/api/v1/product/category/{self.cake_category.id}/',
                    f'http://127.0.0.1:8000/api/v1/product/category/{new_category.id}/'
                ]
            }
            response = self.view_post(
                data=product_data,
                format='multipart',
                HTTP_AUTHORIZATION=f'Bearer {self.state_full_token.get("access")}'
            )

        self.assertTrue(Product.objects.filter(
            name=product_data.get('name'),
            price=product_data.get('price'),
            is_available=product_data.get('is_available')
        ).exists())

        self.assertEqual(Category.objects.filter(product_set__name=product_data.get('name')).count(), 2)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 5)
        self.assertEqual(Product.objects.filter(categories__name='cake').count(), 4)
        self.assertEqual(Product.objects.filter(categories__name='new category').count(), 1)

    def test_not_to_create_product_by_user_is_not_staff(self):
        simple_user_field = {
            'mobile_number': '09103791345',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir'
        }
        simple_user = User.objects.create_user(**simple_user_field)
        simple_user_state_full_token = generate_state_full_jwt(user=simple_user)
        product_data = {
            'name': 'new cake',
            'price': 254,
            'is_available': True,
        }
        response = self.view_post(
            data=product_data,
            format='multipart',
            HTTP_AUTHORIZATION=f'Bearer {simple_user_state_full_token.get("access")}'
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Product.objects.count(), 4)


class TestProductDetailView(APITransactionTestCase):
    view_name = 'product-detail'
    reset_sequences = True


    @classmethod
    def setUp(self):
        self.user_fields = {
            'mobile_number': '09103791346',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir'
        }
        self.staff_user = User.objects.create_user(**self.user_fields, is_staff=True)
        self.state_full_token = generate_state_full_jwt(user=self.staff_user)
        self.cake_category = Category(name='cake', )
        self.cake_category.save(user=self.staff_user)
        self.cake_category_product_list = [
            Product(name='simple cake', price=100, is_available=True),
            Product(name='chocolate cake', price=150, is_available=False),
            Product(name='vanilla cake', price=143, is_available=True),
        ]
        for product in self.cake_category_product_list:
            product.save(user=self.staff_user)
            product.categories.set([self.cake_category])
        self.other_product = [
            Product(name='other', price=250, is_available=True),
        ]
        self.other_product[0].save(user=self.staff_user)

    def test_get_detail_product(self):
        response = self.view_get(reverse_kwargs={'pk': self.cake_category_product_list[0].id})
        self.assertEqual(response.status_code, 200)
        product = self.cake_category_product_list[0]
        self.assertEqual(product.id, response.data.get('id'))
        self.assertEqual(product.name, response.data.get('name'))
        self.assertIn('image', response.data)
        self.assertIn('categories', response.data)
        self.assertIn('create_date', response.data)
        self.assertIn('update_date', response.data)

    def test_update_product(self):
        with open('/home/ubunto/Public/programming/python/django/tests/shop/Product/test/img.png') as image_file:
            image_file_data = image_file.buffer.read()
            image_file = BytesIO(image_file_data)
            image_file.name = 'new_cake.png'
            product_data = {
                'name': 'new cake',
                'price': 254,
                'image': image_file,
                'is_available': True,
            }
            response = self.view_put(
                data=product_data,
                format='multipart',
                reverse_kwargs={'pk': self.cake_category_product_list[0].id},
                HTTP_AUTHORIZATION=f'Bearer {self.state_full_token.get("access")}'
            )

        updated_product_in_db = Product.objects.get(id=1)
        self.assertEqual(product_data.get('name'), updated_product_in_db.name)
        self.assertEqual(product_data.get('price'), updated_product_in_db.price)
        self.assertEqual(product_data.get('is_available'), updated_product_in_db.is_available)
        self.assertEqual(image_file_data, updated_product_in_db.image.file.read())
        self.assertEqual(response.status_code, 200)

    def test_update_part_of_product(self):
        with open('/home/ubunto/Public/programming/python/django/tests/shop/Product/test/img.png') as image_file:
            image_file_data = image_file.buffer.read()
            image_file = BytesIO(image_file_data)
            image_file.name = 'new_cake.png'
            product_data = {
                'name': 'new cake',
                'image': image_file,
            }
            response = self.view_patch(
                data=product_data,
                format='multipart',
                reverse_kwargs={'pk': self.cake_category_product_list[0].id},
                HTTP_AUTHORIZATION=f'Bearer {self.state_full_token.get("access")}'
            )

        updated_product_in_db = Product.objects.get(id=1)
        updated_product = self.cake_category_product_list[0]
        self.assertEqual(product_data.get('name'), updated_product_in_db.name)
        self.assertEqual(image_file_data, updated_product_in_db.image.file.read())
        self.assertEqual(updated_product.price, updated_product_in_db.price)
        self.assertEqual(updated_product.is_available, updated_product_in_db.is_available)
        self.assertEqual(Product.objects.filter(categories__name='cake').count(), 3)
        self.assertEqual(updated_product_in_db.categories.count(), 1)

        self.assertEqual(response.status_code, 200)

    def test_update_product_with_category(self):
        new_category = Category.objects.create(name='new category')
        with open('/home/ubunto/Public/programming/python/django/tests/shop/Product/test/img.png') as image_file:
            image_file_data = image_file.buffer.read()
            image_file = BytesIO(image_file_data)
            image_file.name = 'new_cake.png'
            product_data = {
                'name': 'new cake',
                'price': 254,
                'image': image_file,
                'is_available': True,
                'categories': [
                    f'http://127.0.0.1:8000/api/v1/product/category/{new_category.id}/',
                    f'http://127.0.0.1:8000/api/v1/product/category/{self.cake_category.id}/'
                ]
            }
            response = self.view_put(
                data=product_data,
                format='multipart',
                reverse_kwargs={'pk': self.cake_category_product_list[0].id},
                HTTP_AUTHORIZATION=f'Bearer {self.state_full_token.get("access")}'
            )
        updated_product_in_db = Product.objects.get(name=product_data.get('name'))
        self.assertEqual(product_data.get('name'), updated_product_in_db.name)
        self.assertEqual(product_data.get('price'), updated_product_in_db.price)
        self.assertEqual(product_data.get('is_available'), updated_product_in_db.is_available)
        self.assertEqual(image_file_data, updated_product_in_db.image.file.read())

        self.assertEqual(updated_product_in_db.categories.count(), 2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Product.objects.filter(categories__name='cake').count(), 3)
        self.assertEqual(Product.objects.filter(categories__name='new category').count(), 1)

    def test_update_product_with_no_categories(self):
        pk = self.cake_category_product_list[0].id
        with open('/home/ubunto/Public/programming/python/django/tests/shop/Product/test/img.png') as image_file:
            image_file_data = image_file.buffer.read()
            image_file = BytesIO(image_file_data)
            image_file.name = 'new_cake.png'
            product_data = {
                'name': 'new cake',
                'price': 254,
                'image': image_file,
                'is_available': True,
                'categories': [
                ]
            }
            response = self.view_put(
                data=product_data,
                format='multipart',
                reverse_kwargs={'pk': pk},
                HTTP_AUTHORIZATION=f'Bearer {self.state_full_token.get("access")}'
            )
        updated_product_in_db = Product.objects.get(name=product_data.get('name'))
        self.assertEqual(product_data.get('name'), updated_product_in_db.name)
        self.assertEqual(product_data.get('price'), updated_product_in_db.price)
        self.assertEqual(product_data.get('is_available'), updated_product_in_db.is_available)
        self.assertEqual(image_file_data, updated_product_in_db.image.file.read())

        self.assertEqual(updated_product_in_db.categories.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Product.objects.count(), 4)
        self.assertEqual(Product.objects.filter(categories__name='cake').count(), 2)

    def test_update_product_with_no_category_field(self):
        pk = self.cake_category_product_list[0].id
        with open('/home/ubunto/Public/programming/python/django/tests/shop/Product/test/img.png') as image_file:
            image_file_data = image_file.buffer.read()
            image_file = BytesIO(image_file_data)
            image_file.name = 'new_cake.png'
            product_data = {
                'name': 'new cake',
                'price': 254,
                'image': image_file,
                'is_available': True,
            }
            response = self.view_put(
                data=product_data,
                format='multipart',
                reverse_kwargs={'pk': pk},
                HTTP_AUTHORIZATION=f'Bearer {self.state_full_token.get("access")}'
            )
        updated_product_in_db = Product.objects.get(name=product_data.get('name'))
        self.assertEqual(product_data.get('name'), updated_product_in_db.name)
        self.assertEqual(product_data.get('price'), updated_product_in_db.price)
        self.assertEqual(product_data.get('is_available'), updated_product_in_db.is_available)
        self.assertEqual(image_file_data, updated_product_in_db.image.file.read())

        self.assertEqual(updated_product_in_db.categories.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Product.objects.count(), 4)
        self.assertEqual(Product.objects.filter(categories__name='cake').count(), 2)

    def test_not_to_update_product_by_user_is_not_staff(self):
        pk = self.cake_category_product_list[1].id
        simple_user_field = {
            'mobile_number': '09103791345',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir'
        }
        simple_user = User.objects.create_user(**simple_user_field)
        simple_user_state_full_token = generate_state_full_jwt(user=simple_user)
        with open('/home/ubunto/Public/programming/python/django/tests/shop/Product/test/img.png') as image_file:
            image_file_data = image_file.buffer.read()
            image_file = BytesIO(image_file_data)
            image_file.name = 'new_cake.png'
            product_data = {
                'name': 'new cake',
                'price': 254,
                'image': image_file,
                'is_available': True,
            }
            response = self.view_put(
                data=product_data,
                format='multipart',
                reverse_kwargs={'pk': pk},
                HTTP_AUTHORIZATION=f'Bearer {simple_user_state_full_token.get("access")}'
            )
        self.assertFalse(Product.objects.filter(name=product_data.get('name')).exists())
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Product.objects.count(), 4)

    def test_delete_product(self):
        pk = self.cake_category_product_list[1].id
        response = self.view_delete(
            reverse_kwargs={'pk': pk},
            HTTP_AUTHORIZATION=f'Bearer {self.state_full_token.get("access")}'
        )

        deleted_product = self.cake_category_product_list[pk - 1]
        self.assertFalse(Product.objects.filter(name=deleted_product.name).exists())
        self.assertEqual(Product.objects.all().count(), 3)
        self.assertEqual(response.status_code, 204)

    def test_not_to_delete_product_by_user_is_not_staff(self):
        pk = self.cake_category_product_list[1].id
        simple_user_field = {
            'mobile_number': '09103791345',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir'
        }
        simple_user = User.objects.create_user(**simple_user_field)
        simple_user_state_full_token = generate_state_full_jwt(user=simple_user)
        response = self.view_delete(
            reverse_kwargs={'pk': pk},
            HTTP_AUTHORIZATION=f'Bearer {simple_user_state_full_token.get("access")}'
        )

        not_deleted_product = self.cake_category_product_list[pk - 1]
        self.assertTrue(Product.objects.filter(name=not_deleted_product.name).exists())
        self.assertEqual(Product.objects.all().count(), 4)
        self.assertEqual(response.status_code, 403)


class TestCategoryListView(APITransactionTestCase):
    view_name = 'category-list'
    reset_sequences = True


    def setUp(self):
        self.user_fields = {
            'mobile_number': '09103791346',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir'
        }
        self.staff_user = User.objects.create_user(**self.user_fields, is_staff=True)
        self.state_full_token = generate_state_full_jwt(user=self.staff_user)
        self.cake_category = Category(name='cake', )
        self.car_category = Category(name='car', )
        self.cake_category.save(user=self.staff_user)
        self.car_category.save(user=self.staff_user)

    def test_get_category_list_view(self):
        response = self.view_get()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('count'), 2)
        self.assertIn('results', response.data)

        response = self.view_get(query_string='name=cake')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('count'), 1)
        self.assertIn('results', response.data)

    def test_creat_category(self):
        category_data = {'name': 'new category'}
        response = self.view_post(
            data=category_data,
            HTTP_AUTHORIZATION=f'Bearer {self.state_full_token.get("access")}'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Category.objects.count(), 3)

    def test_not_to_create_category_by_user_is_not_staff(self):
        simple_user_field = {
            'mobile_number': '09103791345',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir'
        }
        simple_user = User.objects.create_user(**simple_user_field)
        simple_user_state_full_token = generate_state_full_jwt(user=simple_user)
        category_data = {
            'name': 'new category',
        }
        response = self.view_post(
            data=category_data,
            HTTP_AUTHORIZATION=f'Bearer {simple_user_state_full_token.get("access")}'
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Category.objects.count(), 2)
        self.assertFalse(Category.objects.filter(name=category_data.get('name')).exists())


class TestCategoryDetailView(APITransactionTestCase):
    view_name = 'category-detail'
    reset_sequences = True


    def setUp(self):
        self.user_fields = {
            'mobile_number': '09103791346',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir'
        }
        self.staff_user = User.objects.create_user(**self.user_fields, is_staff=True)
        self.state_full_token = generate_state_full_jwt(user=self.staff_user)
        self.cake_category = Category(name='cake', )
        self.car_category = Category(name='car', )
        self.cake_category.save(user=self.staff_user)
        self.car_category.save(user=self.staff_user)
        self.categories = [self.cake_category, self.car_category]
        self.new_category_data = {
            'name': 'new category',
        }
        self.pk = self.cake_category.id

    def test_get_detail_category(self):
        response = self.view_get(reverse_kwargs={'pk': self.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.cake_category.id, response.data.get('id'))
        self.assertEqual(self.cake_category.name, response.data.get('name'))
        self.assertIn('create_date', response.data)
        self.assertIn('update_date', response.data)

    def test_update_category(self):
        response = self.view_put(
            data=self.new_category_data,
            reverse_kwargs={'pk': self.pk},
            HTTP_AUTHORIZATION=f'Bearer {self.state_full_token.get("access")}'
        )

        updated_category_in_db = Category.objects.get(id=self.pk)
        self.assertEqual(self.new_category_data.get('name'), updated_category_in_db.name)
        self.assertEqual(response.status_code, 200)

    def test_update_part_of_category(self):
        response = self.view_patch(
            data=self.new_category_data,
            reverse_kwargs={'pk': self.pk},
            HTTP_AUTHORIZATION=f'Bearer {self.state_full_token.get("access")}'
        )

        updated_category_in_db = Category.objects.get(id=self.pk)
        self.assertEqual(self.new_category_data.get('name'), updated_category_in_db.name)
        self.assertEqual(Category.objects.count(), len(self.categories))
        self.assertEqual(response.status_code, 200)

    def test_not_to_update_category_by_user_is_not_staff(self):
        simple_user_field = {
            'mobile_number': '09103791345',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir'
        }
        simple_user = User.objects.create_user(**simple_user_field)
        simple_user_state_full_token = generate_state_full_jwt(user=simple_user)
        response = self.view_put(
            data=self.new_category_data,
            reverse_kwargs={'pk': self.pk},
            HTTP_AUTHORIZATION=f'Bearer {simple_user_state_full_token.get("access")}',
        )
        self.assertFalse(Category.objects.filter(name=self.new_category_data.get('name')).exists())
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Category.objects.count(), len(self.categories))

    def test_delete_category(self):
        category_to_delete = self.categories[0]
        pk = category_to_delete.id
        response = self.view_delete(
            reverse_kwargs={'pk': pk},
            HTTP_AUTHORIZATION=f'Bearer {self.state_full_token.get("access")}'
        )

        self.assertFalse(Category.objects.filter(name=category_to_delete.name).exists())
        self.assertEqual(Category.objects.all().count(), len(self.categories) - 1)
        self.assertEqual(response.status_code, 204)

    def test_not_to_delete_product_by_user_is_not_staff(self):
        not_category_to_delete = self.categories[0]
        pk = not_category_to_delete.id
        simple_user_field = {
            'mobile_number': '09103791345',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir'
        }
        simple_user = User.objects.create_user(**simple_user_field)
        simple_user_state_full_token = generate_state_full_jwt(user=simple_user)
        response = self.view_delete(
            reverse_kwargs={'pk': pk},
            HTTP_AUTHORIZATION=f'Bearer {simple_user_state_full_token.get("access")}'
        )

        self.assertTrue(Category.objects.filter(name=not_category_to_delete.name).exists())
        self.assertEqual(Category.objects.all().count(), len(self.categories))
        self.assertEqual(response.status_code, 403)
