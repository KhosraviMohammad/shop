from django.test import TestCase, TransactionTestCase
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory
from rest_framework.reverse import reverse


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


class APIRequestTestCaseMixin:
    api = APIRequestFactory()

    view_name = None

    request_post = api_action_wrapper("post")
    request_get = api_action_wrapper("get")
    request_put = api_action_wrapper("put")
    request_delete = api_action_wrapper("delete")


class APIViewTestCaseMixin:
    api = APIClient()
    view_post = api_action_wrapper("post")
    view_get = api_action_wrapper("get")
    view_put = api_action_wrapper("put")
    view_patch = api_action_wrapper("patch")
    view_delete = api_action_wrapper("delete")
    view_name = None

    def authenticate_with_token(self, type, token):
        """
        Authenticates requests with the given token.
        """
        self.api.credentials(HTTP_AUTHORIZATION=f"{type} {token}")


class APIViewTestCase(TestCase, APIViewTestCaseMixin):
    client_class = APIClient


class APIRequestTestCase(TestCase, APIRequestTestCaseMixin):
    client_class = APIClient


class APITransactionTestCase(TransactionTestCase, APIViewTestCaseMixin):
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
    view_patch = api_action_wrapper("patch")
    view_delete = api_action_wrapper("delete")
