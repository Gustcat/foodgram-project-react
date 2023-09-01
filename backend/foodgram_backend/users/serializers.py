from djoser.serializers import UserSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Subscription


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField('get_is_subscribed',
                                                      read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        is_subscribed = Subscription.objects.filter(subscriber=current_user, subscribing=obj).exists()
        return is_subscribed


class SubscriptionSerializer(serializers.ModelSerializer):
    subscribing = CustomUserSerializer
    # recipes = serializers.SerializerMethodField()
    # recipes_count = serializers.SerializerMethodField('get_recipes_count',
    #                                                   read_only=True)

    class Meta:
        model = Subscription
        fields = 'subscribing', 'recipes', 'recipes_count'


    # def get_recipes_count(self, obj):
    #     recipes = obj.recipes.all()
    #     return recipes.count()
