from django.db import models
from django.core.validators import FileExtensionValidator

import uuid

# Create your models here.


def custom_upload_to(instance, filename):
    return f"{str(uuid.uuid4())}__{filename}"


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
        upload_to=custom_upload_to,
    )
    script_title = models.CharField(
        max_length=50,
    )
    origin_script = models.TextField(
        default="",
    )
    modified_script = models.TextField(
        default="",
    )
    summary_script = models.TextField(
        default="",
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
