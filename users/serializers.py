from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from users.models import User
from users.fields import PasswordField


class CreateUserSerializer(serializers.ModelSerializer):
    password = PasswordField(required=True)
    password_repeat = PasswordField(required=True)

    class Meta:
        model = User
        exclude = ['is_staff', 'is_active', 'date_joined']

    def validate(self, attrs: dict) -> dict:
        if attrs['password'] != attrs['password_repeat']:
            raise ValidationError('Пароли не совпадают')
        return attrs

    def create(self, validated_data: dict) -> User:
        del validated_data['password_repeat']
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class LoginSerializer(serializers.ModelSerializer):
    password = PasswordField(required=True)
    username = serializers.CharField(max_length=20)

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data: dict) -> User:
        if not(user := authenticate(
            username=validated_data['username'],
            password=validated_data['password']
        )):
            raise AuthenticationFailed('Неправильный логин или пароль')
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class PasswordUpdateSerializer(serializers.Serializer):
    old_password = PasswordField(required=True)
    new_password = PasswordField(required=True)

    def validate(self, attrs: dict) -> dict:
        if not self.instance.check_password(attrs['old_password']):
            raise ValidationError(detail='Passwords must match')
        return attrs

    def update(self, instance: User, validated_data: dict) -> User:
        instance.set_password(validated_data['new_password'])
        instance.save(update_fields=['password'])
        return instance
