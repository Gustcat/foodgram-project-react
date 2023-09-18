from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Subscription


User = get_user_model()


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'subscribing',)
    search_fields = ('subscriber', 'subscribing',)
    list_filter = ('subscriber', 'subscribing',)


class UserAdmin(admin.ModelAdmin):
    list_display = list_display = ('username', 'email', 'first_name',
                                   'last_name', 'is_active', 'is_superuser',
                                   'is_staff', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
