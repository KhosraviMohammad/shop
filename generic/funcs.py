from rest_framework_simplejwt.tokens import RefreshToken
from BaseUser.tokens import GenericAccessToken



def generate_state_full_jwt(user):
    '''
    it generates state-full token for given user

    state-full token means the token will be stored in DB

    :param user:
    :return: {access:access, refresh}
    '''
    data = {}
    refresh = RefreshToken.for_user(user)
    access = GenericAccessToken.for_user(user)
    data["refresh"] = str(refresh)
    data["access"] = str(access)
    return data
