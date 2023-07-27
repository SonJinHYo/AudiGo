from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    username = models.CharField(
        max_length=30,
        default="",
    )
    created_at = models.DateTimeField()
    using_gpt_roken = models.PositiveIntegerField()
