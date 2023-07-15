from rest_framework_simplejwt.tokens import AccessToken, BlacklistMixin


class GenericAccessToken(BlacklistMixin, AccessToken):
    pass
