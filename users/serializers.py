from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import User
from scripts.models import Audio
from scripts.serializers import TinyAudioSerializer


class UserSerializer(ModelSerializer):
    audios = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "using_gpt_token",
            "rem_gpt_token",
            "audios",
        )

    def get_audios(self, user):
        return TinyAudioSerializer(
            Audio.objects.filter(user=user),
            many=True,
        ).data
