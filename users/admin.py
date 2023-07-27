from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "created_at",
        "using_gpt_token",
        "rem_gpt_token",
    )
