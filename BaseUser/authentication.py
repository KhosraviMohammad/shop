from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from BaseUser.models import BlackListedAccessToken, OutstandingAccessToken


class CustomJWTAuthentication(JWTAuthentication):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header.
    """

    www_authenticate_realm = "api"
    media_type = "application/json"

    def authenticate(self, request):
        data = super(CustomJWTAuthentication, self).authenticate(request)
        if data is not None:
            (user, auth) = data
            self.validate_token(auth)
        return data

    def validate_token(self, auth):
        if BlackListedAccessToken.objects.filter(token=auth.token.decode()).exists() or not OutstandingAccessToken.objects.filter(token=auth.token.decode()).exists():
            raise InvalidToken(_("تکن نامعتبر میباشد"))
