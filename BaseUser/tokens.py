from rest_framework_simplejwt.tokens import AccessToken, BlacklistMixin


class GenericAccessToken(BlacklistMixin, AccessToken):
    '''
    customized access token

    purpose of it is to add capable of blocking to AccessToken
    '''
