from django.contrib import admin
from .models import Subscription


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'subscribing',)
    search_fields = ('subscriber', 'subscribing',)
    list_filter = ('subscriber', 'subscribing',)


admin.site.register(Subscription, SubscriptionAdmin)
