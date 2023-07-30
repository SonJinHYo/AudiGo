from django.urls import path
from . import views

urlpatterns = [
    path("", views.Me.as_view()),
    path("me", views.MyScript.as_view()),
    path("login", views.LogIn.as_view()),
    path("logout", views.LogOut.as_view()),
    path("kakao", views.KakaoLogIn.as_view()),
]
