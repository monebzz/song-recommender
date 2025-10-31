from rest_framework import serializers
from .models import Song, UserProfile, Subscription, Purchase
from django.contrib.auth.models import User


class SongSerializer(serializers.ModelSerializer):
    sentiment_label = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = [
            'id',
            'deezer_id',
            'title',
            'artist',
            'album',
            'link',
            'preview',
            'cover',
            'sentiment',
            'sentiment_label',
            'created_at',
        ]

    def get_sentiment_label(self, obj):
        if obj.sentiment is None:
            return "Unknown"
        
        from .utils import SentimentAnalyzer
        return SentimentAnalyzer.get_sentiment_label(obj.sentiment)


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    has_active_subscription = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'username',
            'daily_usage_count',
            'last_usage_date',
            'has_active_subscription',
        ]

    def get_has_active_subscription(self, obj):
        return obj.has_active_subscription()


class SubscriptionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id',
            'username',
            'plan_type',
            'start_date',
            'end_date',
            'active',
            'created_at',
        ]


class PurchaseSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Purchase
        fields = [
            'id',
            'username',
            'plan_type',
            'amount',
            'status',
            'created_at',
        ]


class CheckoutSerializer(serializers.Serializer):
    plan_type = serializers.ChoiceField(choices=['monthly', 'yearly'])

    def validate_plan_type(self, value):
        if value not in ['monthly', 'yearly']:
            raise serializers.ValidationError("Invalid plan type")
        return value

