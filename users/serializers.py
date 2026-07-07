from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(min_length=5, max_length=20, validators=[
        RegexValidator(regex=r"^[a-zA-Z0-9]+[a-zA-Z_0-9]*[a-zA-Z0-9]+$",
                       message='Логин содержит недопустимые символы'), UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, min_length=8, max_length=20, validators=[
        RegexValidator(regex=r"^[a-zA-Z0-9!@#$%^&*(),.?\":{}|<>[\]/`~+=-_';]*$",
                       message='Пароль содержит недопустимые символы')])

    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        return User.objects.create_user(username=validated_data['username'], password=validated_data['password'])

    def validate(self, data):
        password = data.get('password')
        user = User(username=data.get('username'))
        try:
            validate_password(password, user)
        except ValidationError as e:
            raise serializers.ValidationError({'password': e.messages})
        return data


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=5, max_length=20, validators=[
        RegexValidator(regex=r"^[a-zA-Z0-9]+[a-zA-Z_0-9]*[a-zA-Z0-9]+$",
                       message='Логин содержит недопустимые символы')])
    password = serializers.CharField(min_length=8, max_length=20, validators=[
        RegexValidator(regex=r"^[a-zA-Z0-9!@#$%^&*(),.?\":{}|<>[\]/`~+=-_';]*$",
                       message='Пароль содержит недопустимые символы')])
