from django.db.models import Q
from rest_registration.auth_token_managers import AbstractAuthTokenManager

from rest_framework_simplejwt.token_blacklist.models import OutstandingToken as OutstandingRefreshToken, \
    BlacklistedToken as BlacklistedRefreshToken

from BaseUser.authentication import CustomJWTAuthentication
from BaseUser.models import OutstandingAccessToken, BlackListedAccessToken
from generic.funcs import generate_state_full_jwt


class JWTAuthTokenManager(AbstractAuthTokenManager):

    def __init__(self, *args, **kwargs):
        super(JWTAuthTokenManager, self).__init__(*args, **kwargs)

    def get_authentication_class(self):
        return CustomJWTAuthentication

    def revoke_token(self, user, token=None):
        '''

        it bocks all refresh and access tokens which stored in database

        :param user:
        :param token:
        :return:
        '''

        # blocking all access_token
        outstanding_access_token_qu = OutstandingAccessToken.objects.filter(user=user)
        black_list_access_qu = BlackListedAccessToken.objects.filter(user=user).values('token')
        black_list_access_qu_to_block = outstanding_access_token_qu.filter(~Q(token__in=black_list_access_qu)).values(
            'token')
        black_list_access_obj_ls = []
        for token in black_list_access_qu_to_block:
            black_list_access_obj_ls.append(BlackListedAccessToken(token=token.get('token'), user=user))
        BlackListedAccessToken.objects.bulk_create(black_list_access_obj_ls)

        # blocking all refresh_token
        outstanding_refresh_token_qu_to_block = OutstandingRefreshToken.objects.filter(blacklistedtoken=None, user=user)
        black_list_refresh_obj_ls = []
        for token in outstanding_refresh_token_qu_to_block:
            black_list_refresh_obj_ls.append(BlacklistedRefreshToken(token=token))
        BlacklistedRefreshToken.objects.bulk_create(black_list_refresh_obj_ls)

    def provide_token(self, user: 'AbstractBaseUser'):

        state_full_jwt = generate_state_full_jwt(user)

        return state_full_jwt
