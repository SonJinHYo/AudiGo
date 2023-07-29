from rest_framework.serializers import ModelSerializer
from .models import Audio, Charecter
from users.serializers import UsernameSerializer


class TinyAudioSerializer(ModelSerializer):
    class Meta:
        model = Audio
        fields = ("title",)


class DetailAudioSerializer(ModelSerializer):
    class Meta:
        model = Audio
        fields = (
            "title",
            "origin_script",
            "modified_script",
        )


class AudioFirstSaveSerializer(ModelSerializer):
    class Meta:
        model = Audio
        fields = (
            "user",
            "file",
            "title",
        )
