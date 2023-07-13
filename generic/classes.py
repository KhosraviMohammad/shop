import traceback
from django.test import TestCase

from rest_framework.permissions import IsAdminUser, SAFE_METHODS

from rest_framework import serializers
from rest_framework.utils import model_meta
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory
from rest_framework.reverse import reverse

from BaseUser.models import BaseUserFieldModel


class IsAdminUserOrReadOnlyPermission(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS or
                    super(IsAdminUserOrReadOnlyPermission, self).has_permission(request, view))


class GenericHyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):

    def __init__(self, *args, **kwargs):
        super(GenericHyperlinkedModelSerializer, self).__init__(*args, **kwargs)
        assert issubclass(self.Meta.model, BaseUserFieldModel), \
            f'{type(self).__name__}.Meta.model does not inheritance from BaseUserFieldModel'

    def create(self, validated_data):

        serializers.raise_errors_on_nested_writes('create', self, validated_data)

        ModelClass = self.Meta.model

        # Remove many-to-many relationships from validated_data.
        # They are not valid arguments to the default `.create()` method,
        # as they require that the instance has already been saved.
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            instance = ModelClass(**validated_data)
            instance.save(user=self.context['request'].user)
        except TypeError:
            tb = traceback.format_exc()
            msg = (
                    'Got a `TypeError` when calling `%s.%s.create()`. '
                    'This may be because you have a writable field on the '
                    'serializer class that is not a valid argument to '
                    '`%s.%s.create()`. You may need to make the field '
                    'read-only, or override the %s.create() method to handle '
                    'this correctly.\nOriginal exception was:\n %s' %
                    (
                        ModelClass.__name__,
                        ModelClass._default_manager.name,
                        ModelClass.__name__,
                        ModelClass._default_manager.name,
                        self.__class__.__name__,
                        tb
                    )
            )
            raise TypeError(msg)

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in many_to_many.items():
                field = getattr(instance, field_name)
                field.set(value)

        return instance

    def update(self, instance, validated_data):

        serializers.raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save(user=self.context['request'].user)

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance


def api_action_wrapper(action):
    def wrapper_method(self, *args, **kwargs):
        if self.view_name is None:
            raise ValueError("Must give value for `view_name` property")

        reverse_args = kwargs.pop("reverse_args", tuple())
        reverse_kwargs = kwargs.pop("reverse_kwargs", dict())
        query_string = kwargs.pop("query_string", None)

        url = reverse(self.view_name, args=reverse_args, kwargs=reverse_kwargs)
        if query_string is not None:
            url = url + f"?{query_string}"

        return getattr(self.api, action)(url, *args, **kwargs)

    return wrapper_method


class GenericTestCase(TestCase):
    pass


class APIViewTestCase(GenericTestCase):
    client_class = APIClient

    api = APIClient()

    def authenticate_with_token(self, type, token):
        """
        Authenticates requests with the given token.
        """
        self.api.credentials(HTTP_AUTHORIZATION=f"{type} {token}")

    view_name = None

    view_post = api_action_wrapper("post")
    view_get = api_action_wrapper("get")
    view_put = api_action_wrapper("put")
    view_delete = api_action_wrapper("delete")


class APIRequestTestCase(GenericTestCase):
    client_class = APIClient

    api = APIRequestFactory()

    view_name = None

    request_post = api_action_wrapper("post")
    request_get = api_action_wrapper("get")
    request_put = api_action_wrapper("put")
    request_delete = api_action_wrapper("delete")
