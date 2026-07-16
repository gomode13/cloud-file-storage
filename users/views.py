from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from config.exceptions import Conflict
from users.models import User
from users.serializers import SignUpSerializer, SignInSerializer


# Create your views here.

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'username': request.user.username}, status=status.HTTP_200_OK)


class SignOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SignUpView(APIView):

    def post(self, request):
        username = request.data.get('username')
        if User.objects.filter(username=username).exists():
            raise Conflict('Такой пользователь уже существует')
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
        except IntegrityError:
            raise Conflict('Такой пользователь уже существует')
        login(request, user)
        return Response({'username': username}, status=status.HTTP_201_CREATED)


class SignInView(APIView):
    def post(self, request):
        serializer = SignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, username=serializer.validated_data['username'],
                            password=serializer.validated_data['password'])
        if user is not None:
            login(request, user)
            return Response({'username': user.username}, status=status.HTTP_200_OK)
        else:
            raise AuthenticationFailed('Неверный логин или пароль')

