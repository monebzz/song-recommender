from django.contrib import admin
from .models import Song, UserProfile, Subscription, Purchase


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'album', 'sentiment', 'created_at']
    search_fields = ['title', 'artist', 'album', 'deezer_id']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'daily_usage_count', 'last_usage_date', 'has_active_subscription']
    search_fields = ['user__username', 'user__email']
    list_filter = ['last_usage_date']

    def has_active_subscription(self, obj):
        return obj.has_active_subscription()
    has_active_subscription.boolean = True
    has_active_subscription.short_description = 'Active Subscription'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan_type', 'active', 'start_date', 'end_date', 'created_at']
    search_fields = ['user__username', 'user__email', 'stripe_payment_intent_id']
    list_filter = ['plan_type', 'active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan_type', 'amount', 'status', 'created_at']
    search_fields = ['user__username', 'user__email', 'stripe_payment_intent_id']
    list_filter = ['plan_type', 'status', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
