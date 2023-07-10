from rest_framework import generics
from rest_framework.response import Response

from BaseUser.serializers import BlockAccessTokenSerializer
from django.utils.translation import gettext_lazy as _


# Create your views here.

class AccessTokenBlockView(generics.GenericAPIView):
    serializer_class = BlockAccessTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response({'message': _('خارج شدیند')}, status=200)
