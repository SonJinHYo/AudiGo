from django.db import models

# Create your models here.


class Audio(models.Model):
    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
    )
    data_url = models.URLField()
    title = models.CharField()
    origin_script = models.TextField()
    modified_script = models.TextField()
    create_at = models.DateTimeField()


class Charecter(models.Model):
    script = models.ForeignKey(
        "Audios",
        on_delete=models.CASCADE,
    )
    start_time = models.FloatField()
    end_time = models.FloatField()
    confidence = models.FloatField()
    content = models.CharField()
    type = models.CharField()
