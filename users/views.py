from django.db import IntegrityError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, authenticate, logout
from users.serializers import SignUpSerializer, SignInSerializer


# Create your views here.

@api_view(['POST'])
def sign_up(request):
    serializer = SignUpSerializer(data=request.data)

    if serializer.is_valid():
        try:
            user = serializer.save()
        except IntegrityError:
            return Response({'message': 'Такой пользователь уже существует'}, status=status.HTTP_409_CONFLICT)
        login(request, user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        error = list(serializer.errors.values())[0][0]
        if error.code == 'unique':
            return Response({'message': 'Такой пользователь уже существует'}, status=status.HTTP_409_CONFLICT)
        return Response({'message': error}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def sign_in(request):
    serializer = SignInSerializer(data=request.data)
    if serializer.is_valid():
        user = authenticate(request, username=serializer.validated_data['username'],
                            password=serializer.validated_data['password'])
        if user is not None:
            login(request, user)
            return Response({'username': user.username}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Неверный логин или пароль'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        error = list(serializer.errors.values())[0][0]
        return Response({'message': error}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def sign_out(request):
    if request.user.is_authenticated:
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        return Response({'message': 'Запрос исполняется неавторизованным пользоватаелем'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def current_user(request):
    if request.user.is_authenticated:
        return Response({'username': request.user.username}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Запрос исполняется неавторизованным пользоватаелем'}, status=status.HTTP_401_UNAUTHORIZED)
