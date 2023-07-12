from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import update_last_login

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer, TokenObtainSerializer

from BaseUser.models import User, BlackListedAccessToken, OutstandingAccessToken
from generic.funcs import generate_state_full_jwt


class UserRegisterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'gender', 'last_name', 'mobile_number', 'avatar', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        mobile_number = validated_data.pop('mobile_number')
        with transaction.atomic():
            user = User(username=mobile_number, mobile_number=mobile_number, **validated_data)
            user.set_password(password)
            user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs):
        data = super().validate(attrs)

        state_full_jwt_token = generate_state_full_jwt(self.user)
        data.update(state_full_jwt_token)
        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data


class BlockAccessTokenSerializer(serializers.Serializer):
    access = serializers.CharField()

    def validate(self, attrs):
        data = super().validate(attrs)
        raw_access_token = data.get('access')
        outstanding_access_token_qu = OutstandingAccessToken.objects.filter(token=raw_access_token)
        if outstanding_access_token_qu.exists():
            access_token_obj = api_settings.AUTH_TOKEN_CLASSES[0](raw_access_token)
            user_id = access_token_obj.payload.get('user_id')
            BlackListedAccessToken.objects.get_or_create(token=raw_access_token, user_id=user_id)
        else:
            raise serializers.ValidationError(_('token is not valid'))

        return data
