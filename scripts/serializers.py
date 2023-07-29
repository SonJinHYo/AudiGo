from rest_framework.serializers import ModelSerializer
from .models import Audio


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


class AudioSerializer(ModelSerializer):
    class Meta:
        model = Audio
        fields = (
            "user",
            "file",
            "title",
            "origin_script",
            "modified_script",
        )
