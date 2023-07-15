from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import update_last_login

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer, TokenObtainSerializer
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.exceptions import TokenError

from BaseUser.models import User
from BaseUser.tokens import GenericAccessToken
from generic.funcs import generate_state_full_jwt


class UserRegisterSerializer(serializers.HyperlinkedModelSerializer):
    '''
    UserRegisterSerializer for validating , creating, and updating new user
    '''

    class Meta:
        model = User
        fields = ['first_name', 'gender', 'last_name', 'mobile_number', 'avatar', 'password']

    def create(self, validated_data):
        '''
        create new user

        :param validated_data:
        :return:
        '''
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs):
        '''
        it validates entered data and returns jwt token generated from generate_state_full_jwt

        :param attrs:
        :return:
        '''
        data = super().validate(attrs)

        state_full_jwt_token = generate_state_full_jwt(self.user)
        data.update(state_full_jwt_token)
        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data


class BlockAccessTokenSerializer(serializers.Serializer):
    '''
    this serializer blocks given token when BlockAccessTokenSerializer.is_valid is involved
    '''

    access = serializers.CharField()
    token_class = GenericAccessToken

    def validate(self, attrs):
        '''
        fist it validates given access token and then blocks it

        if a token is invalid, it raises ValidationError

        :param attrs:
        :return:
        '''

        # takes access token obj
        try:
            access = self.token_class(attrs["access"])
        except TokenError:
            raise serializers.ValidationError('Token has wrong type')
        try:
            access.blacklist()
        except AttributeError:
            pass

        return {}
