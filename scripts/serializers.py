from rest_framework.serializers import ModelSerializer
from .models import Audio, Charecter


class TinyAudioSerializer(ModelSerializer):
    class Meta:
        model = Audio
        fields = (
            "title",
            "create_at",
        )


class DetailAudioSerializer(ModelSerializer):
    class Meta:
        model = Audio
        fields = (
            "title",
            "origin_script",
            "modified_script",
            "create_at",
        )
