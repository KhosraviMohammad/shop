from django.db.models import Q
from rest_registration.auth_token_managers import AbstractAuthTokenManager

from BaseUser.authentication import CustomJWTAuthentication
from BaseUser.models import OutstandingAccessToken, BlackListedAccessToken


class JWTAuthTokenManager(AbstractAuthTokenManager):

    def __init__(self, *args, **kwargs):
        super(JWTAuthTokenManager, self).__init__(*args, **kwargs)

    def get_authentication_class(self):
        return CustomJWTAuthentication

    def revoke_token(self, user, token=None):
        outstanding_access_token_qu = OutstandingAccessToken.objects.filter(user=user)
        black_list_access_qu = BlackListedAccessToken.objects.filter(user=user).values('token')
        black_list_access_qu_to_block = outstanding_access_token_qu.filter(~Q(token__in=black_list_access_qu)).values('token')
        black_list_access_obj_ls = []
        for token in black_list_access_qu_to_block:
            black_list_access_obj_ls.append(BlackListedAccessToken(token=token.get('token'), user=user))
        BlackListedAccessToken.objects.bulk_create(black_list_access_obj_ls)

    def provide_token(self, user: 'AbstractBaseUser'):
        from rest_framework_simplejwt.tokens import RefreshToken

        data = {}
        refresh = RefreshToken.for_user(user=user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        outstanding_access_token = OutstandingAccessToken(token=data["access"], user=user)
        outstanding_access_token.save()

        return data
