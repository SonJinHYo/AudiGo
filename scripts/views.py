from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import exceptions

from . import serializers
from .models import Audio


class Scripts(APIView):
    permission_classes = [IsAuthenticated]

    def get_objects(self, pk, user):
        try:
            return Audio.objects.get(pk=pk, user=user)
        except:
            raise exceptions.NotFound

    def get(self, pk, request):
        audio = self.get_objects(pk, request.user)
        serializer = serializers.DetailAudioSerializer(audio)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# class UploadAudio(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self,)
