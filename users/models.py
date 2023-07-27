from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    username = models.CharField(
        max_length=30,
        unique=True,
    )
    created_at = models.DateTimeField(
        null=True,
    )
    using_gpt_roken = models.PositiveIntegerField(
        default=0,
    )
