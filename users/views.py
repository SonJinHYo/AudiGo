import time
import uuid
from django.contrib.auth import authenticate, login, logout, get_user

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from scripts.models import Audio

from . import serializers
from .models import User

import requests


class Me(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # serializer = serializers.PrivateUserSerializer(user)
        # return Response(serializer.data)
        return Response({}, status=status.HTTP_200_OK)

    def put(self, request):
        # user = request.user
        # serializer = serializers.PrivateUserSerializer(
        #     user,
        #     data=request.data,
        #     partial=True,
        # )
        # if serializer.is_valid():
        #     user = serializer.save()
        #     serializer = serializers.PrivateUserSerializer(user)
        #     return Response(serializer.data)
        # else:
        #     return Response(serializer.errors)
        return Response()


class MyScript(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Audio.objects.get(pk=pk)
        except Audio.DoesNotExist:
            raise NotFound

    def get(self, request):
        user = request.user
        serializer = serializers.UserSerializer(user)
        return Response(serializer.data)

    def delete(self, request, pk):
        audio = self.get_object(pk=pk)
        audio.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LogIn(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            raise ParseError

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user:
            login(request, user)
            return Response({"ok": "Welcome!"})
        else:
            return Response({"error": "wrong password"})


class LogOut(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"ok": "bye!"})


class KakaoLogIn(APIView):
    def post(self, request):
        try:
            print(1)
            code = request.data.get("code")
            print(code)

            access_token = requests.post(
                "https://kauth.kakao.com/oauth/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "authorization_code",
                    "client_id": "feebe719164baaa0ad0a53aa57e29846",
                    "redirect_uri": "http://ecs-lb-1023174556.ap-northeast-2.elb.amazonaws.com/social/kakao",
                    "code": code,
                },
            )
            print(2)
            access_token = access_token.json().get("access_token")
            print(3)

            user_data = requests.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
                },
            )
            print(4)

            user_data = user_data.json()
            print(5)

            kakao_account = user_data["kakao_account"]
            print(6)

            try:
                print(7)

                user = User.objects.get(email=kakao_account.get("email"))
                print(8)

                login(request, user)
                print(9)

                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                print(10)

                email = kakao_account.get("email")
                print(11)

                user = User.objects.create(
                    email=email,
                    username=str(uuid.uuid1())[:30],
                )
                print(12)

                user.set_unusable_password()
                print(13)

                user.save()
                print(14)

                login(request, user)
                return Response(status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
