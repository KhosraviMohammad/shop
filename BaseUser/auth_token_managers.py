from django.db.models import Q
from rest_registration.auth_token_managers import AbstractAuthTokenManager

from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from BaseUser.authentication import CustomJWTAuthentication
from generic.funcs import generate_state_full_jwt


class JWTAuthTokenManager(AbstractAuthTokenManager):

    def __init__(self, *args, **kwargs):
        super(JWTAuthTokenManager, self).__init__(*args, **kwargs)

    def get_authentication_class(self):
        return CustomJWTAuthentication

    def revoke_token(self, user, token=None):
        '''

        it blocks all refresh and access tokens which stored in database

        :param user:
        :param token:
        :return:
        '''

        # blocking all token
        outstanding_token_qu_to_block = OutstandingToken.objects.filter(blacklistedtoken=None, user=user)
        black_list_token_obj_ls = []
        for token in outstanding_token_qu_to_block:
            black_list_token_obj_ls.append(BlacklistedToken(token=token))
        BlacklistedToken.objects.bulk_create(black_list_token_obj_ls)

    def provide_token(self, user: 'AbstractBaseUser'):
        '''
        it returns generated token

        :param user:
        :return: {access:access, refresh:refresh}
        '''

        state_full_jwt = generate_state_full_jwt(user)

        return state_full_jwt
