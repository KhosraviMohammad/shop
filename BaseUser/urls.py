from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,

)
from BaseUser.views import AccessTokenBlockView

from django.urls import path, include


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('access-token/blacklist/', AccessTokenBlockView.as_view(), name='access_token_blacklist'),
    path('', include('rest_registration.api.urls', namespace='rest-registration')),
]
