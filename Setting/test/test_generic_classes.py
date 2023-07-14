from django.contrib.auth import get_user_model
from django.test.utils import isolate_apps
from django.db import models, connection
from rest_framework.reverse import reverse
from django.urls import resolve

from BaseUser.models import BaseUserFieldModel
from generic.utils_test import APITransactionTestCase, APIRequestFactory, APIRequestTestCase
from generic.funcs import generate_state_full_jwt
from generic.classes import GenericHyperlinkedModelSerializer, IsAdminUserOrReadOnlyPermission

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

    @isolate_apps("Setting")
    def test_raise_error_in_GenericHyperlinkedModelSerializer_by_a_model_not_inheriting_form_BaseUserFieldModel(self):
        class TestModel(models.Model):
            pass

        class TestSerializer(GenericHyperlinkedModelSerializer):
            class Meta:
                model = TestModel
                fields = []

        self.assertRaises(AssertionError, TestSerializer)

    def test_auto_set_user_in_GenericHyperlinkedModelSerializer(self):
        test_data = {'test_field': 'test'}
        request = self.request.post('', data=test_data)
        request.user = self.user

        class TestModel(BaseUserFieldModel):
            test_field = models.CharField(max_length=10)

        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(TestModel)

        class TestSerializer(GenericHyperlinkedModelSerializer):
            class Meta:
                model = TestModel
                fields = ['test_field']

        test_serializer = TestSerializer(data=request.POST, context={'request': request})
        test_serializer.is_valid()
        test_model_to_update = test_serializer.save()

        self.assertTrue(TestModel.objects.filter(
            created_by=self.user,
            updated_by=self.user,
            test_field=test_data.get('test_field')

        ).exists())

        new_user = User.objects.create_user(
            mobile_number='09103791345', first_name='ali', last_name='hasan', password='amir',
        )
        request.user = new_user
        test_serializer = TestSerializer(instance=test_model_to_update, data=request.POST, context={'request': request})
        test_serializer.is_valid()
        test_serializer.save()

        self.assertTrue(TestModel.objects.filter(
            created_by=self.user,
            updated_by=new_user,
            test_field=test_data.get('test_field')

        ).exists())


class TestIsAdminUserOrReadOnlyPermission(APIRequestTestCase):
    view_name = 'product-list'

    def setUp(self) -> None:
        self.user_fields = {
            'mobile_number': '09103791346',
            'first_name': 'Mohammad',
            'last_name': 'Khosravi',
            'password': 'amir',
            'is_staff': True,
        }
        self.user = User.objects.create_user(**self.user_fields)
        self.state_full_token = generate_state_full_jwt(user=self.user)
        self.request = APIRequestFactory()

    # def test_has_permission(self):
    #     request_post = self.request
    #     request_put = self.request
    #     request_get = self.request
    #     request_patch = self.request
    #     request_post.user = self.user
    #     view, args, kwargs = resolve(request.path)
        permission_obj = IsAdminUserOrReadOnlyPermission()
    #     permission_obj.has_permission(request, view.cls)
