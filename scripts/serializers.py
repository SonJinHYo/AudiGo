from rest_framework.serializers import ModelSerializer
from .models import Audio


class TinyAudioSerializer(ModelSerializer):
    class Meta:
        model = Audio
        fields = ("script_title",)


class DetailAudioSerializer(ModelSerializer):
    class Meta:
        model = Audio
        fields = (
            "script_title",
            "origin_script",
            "modified_script",
            "summary_script",
        )


class AudioFirstSaveSerializer(ModelSerializer):
    class Meta:
        model = Audio
        fields = (
            "user",
            "file",
            "script_title",
        )


class AudioSerializer(ModelSerializer):
    class Meta:
        model = Audio
        fields = (
            "user",
            "file",
            "script_title",
            "origin_script",
            "modified_script",
            "summary_script",
        )
