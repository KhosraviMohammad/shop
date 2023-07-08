from django.urls import path


from Setting.views import (
    api_root, api_v1_root, account_api_v1_root
)


urlpatterns = [
    path('', api_root, name='api_root'),
    path('api/v1/', api_v1_root, name='api_v1_root'),

    # api v1 start
    path('api/v1/account', account_api_v1_root, name='account_api_v1_root'),
    # api v1 end

]