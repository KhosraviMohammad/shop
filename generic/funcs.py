from rest_framework_simplejwt.tokens import RefreshToken

from BaseUser.models import OutstandingAccessToken


def generate_state_full_jwt(user):
    data = {}
    refresh = RefreshToken.for_user(user)

    data["refresh"] = str(refresh)
    data["access"] = str(refresh.access_token)
    outstanding_access_token = OutstandingAccessToken(token=data["access"], user=user)
    outstanding_access_token.save()
    return data
