from django.urls import path
from . import views

urlpatterns = [
    path("", views.Me.as_view()),
]
