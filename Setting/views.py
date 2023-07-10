from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


# Create your views here.

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'apis': {
            'api v1': reverse('api_v1_root', request=request, format=format)
        }
    })


@api_view(['GET'])
def api_v1_root(request, format=None):
    return Response({
        'apis': {
            'account api': reverse('account_api_v1_root', request=request, format=format),
            'product api': reverse('product_api_v1_root', request=request, format=format),
        }
    })


@api_view(['GET'])
def account_api_v1_root(request, format=None):
    return Response({
        'apis': {
            'token': reverse('token_obtain_pair', request=request, format=format),
            'token refresh': reverse('token_refresh', request=request, format=format),
            'refresh token blacklist': reverse('token_blacklist', request=request, format=format),
            'access token blacklist': reverse('access_token_blacklist', request=request, format=format),
            'register': reverse('rest-registration:register', request=request, format=format),
            'profile': reverse('rest-registration:profile', request=request, format=format),
            'login': reverse('rest-registration:login', request=request, format=format),
            'logout': reverse('rest-registration:logout', request=request, format=format),
        }
    })


@api_view(['GET'])
def product_api_v1_root(request, format=None):
    return Response({
        'apis': {
            'product': reverse('product-list', request=request, format=format),
            'category': reverse('category-list', request=request, format=format),
        }
    })


