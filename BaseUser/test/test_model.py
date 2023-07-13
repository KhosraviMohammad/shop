from django.contrib.auth import get_user_model

from generic.classes import GenericTestCase

# Create your tests here.

User = get_user_model()


class TestUserModel(GenericTestCase):

    def setUp(self) -> None:
        self.user_fields = {
            'mobile_number': '09103791346',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir'
        }

    def test_user_manger_create(self):
        user = User.objects.create_user(**self.user_fields)
        user_in_db = User.objects.get(mobile_number='09103791346')
        self.assertEqual(user_in_db.username, self.user_fields.get('mobile_number'))
        self.assertEqual(user_in_db.first_name, self.user_fields.get('first_name'))
        self.assertEqual(user_in_db.last_name, self.user_fields.get('last_name'))
        self.assertTrue(user_in_db.check_password(self.user_fields.get('password')))

    def test_user_save(self):
        user = User(**self.user_fields)
        user.set_password(self.user_fields.get('password'))
        user.save()
        user_in_db = User.objects.get(mobile_number='09103791346')
        self.assertEqual(user_in_db.username, self.user_fields.get('mobile_number'))
        self.assertEqual(user_in_db.first_name, self.user_fields.get('first_name'))
        self.assertEqual(user_in_db.last_name, self.user_fields.get('last_name'))
        self.assertTrue(user_in_db.check_password(self.user_fields.get('password')))
