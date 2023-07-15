from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from BaseUser.models import BlackListedAccessToken, OutstandingAccessToken


class CustomJWTAuthentication(JWTAuthentication):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header.

    the purpose of it is to not authenticate user with invalid token which they are not stored in database (stateless token)
    and are stored in black database.table
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
        '''
        it checks if given token is valid otherwise it raises InvalidToken exception

        :param auth:
        :return:
        '''
        if BlackListedAccessToken.objects.filter(
                token=auth.token.decode()).exists() or not OutstandingAccessToken.objects.filter(
            token=auth.token.decode()).exists():
            raise InvalidToken(_("token is not valid"))
