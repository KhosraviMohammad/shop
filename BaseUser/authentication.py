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
            self.validate_token(data[1])
        return data

    def validate_token(self, token):
        if BlackListedAccessToken.objects.filter(token=token.token.decode()).exists():
            raise InvalidToken(
                {
                    "detail": _("Given token not valid"),
                }
            )
