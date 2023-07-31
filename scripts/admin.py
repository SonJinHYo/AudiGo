from django.contrib import admin
from .models import Audio


@admin.register(Audio)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "file",
        "script_title",
    )
