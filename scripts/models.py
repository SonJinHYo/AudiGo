from django.db import models

# Create your models here.


class Audio(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="audios",
    )
    data_url = models.URLField()
    title = models.CharField(max_length=50)
    origin_script = models.TextField()
    modified_script = models.TextField()
    create_at = models.DateTimeField()


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