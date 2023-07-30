from django.urls import path
from . import views

urlpatterns = [
    path("<int:pk>", views.Scripts.as_view()),
    path("create", views.UploadAudio.as_view()),
]
