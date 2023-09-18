from djoser.serializers import UserSerializer, UserCreateSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Subscription


User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('email',
                  'username',
                  'first_name',
                  'last_name',
                  'password',
                  'id')

    def validate(self, attrs):
        required_attrs = ['first_name', 'last_name']
        current_email = attrs.get('email')
        if User.objects.filter(email=current_email).exists():
            raise serializers.ValidationError(
                {'email': ["Уже есть пользователь с таким email."]})
        for required_attr in required_attrs:
            if attrs.get(required_attr) is None:
                raise serializers.ValidationError(
                    {required_attr: ["Это поле обязательно для заполнения."]})
            if attrs.get(required_attr) == '':
                raise serializers.ValidationError(
                    {required_attr: ["Это поле не должно быть пустым."]})
        return super().validate(attrs)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField('get_is_subscribed',
                                                      read_only=True)

    class Meta:
        model = User
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        if current_user.username == '':
            return False
        return Subscription.objects.filter(subscriber=current_user,
                                           subscribing=obj).exists()
