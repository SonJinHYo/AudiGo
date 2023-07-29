from django.db import models
from django.core.validators import FileExtensionValidator

# Create your models here.


class Audio(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="audios",
    )
    file = models.FileField(
        validators=[
            FileExtensionValidator(
                allowed_extensions=["mp3", "mp4", "wav", "flac", "amr", "ogg", "webm"],
            )
        ],
        null=True,
    )
    title = models.CharField(
        max_length=50,
    )
    origin_script = models.TextField(
        null=True,
    )
    modified_script = models.TextField(
        null=True,
    )


class Charecter(models.Model):
    script = models.ForeignKey(
        "scripts.Audio",
        on_delete=models.CASCADE,
        related_name="charecters",
    )
    start_time = models.FloatField()
    end_time = models.FloatField()
    confidence = models.FloatField()
    content = models.CharField(max_length=150)
    type = models.CharField(max_length=20)
