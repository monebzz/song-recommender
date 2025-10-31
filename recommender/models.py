from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Song(models.Model):
    deezer_id = models.CharField(max_length=100, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album = models.CharField(max_length=255, blank=True)
    link = models.URLField()
    preview = models.URLField(blank=True)
    cover = models.URLField(blank=True)
    sentiment = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.artist}"


class UserProfile(models.Model):
    MOOD_CHOICES = [
        ('happy', 'Happy 😊'),
        ('sad', 'Sad 😢'),
        ('energetic', 'Energetic ⚡'),
        ('calm', 'Calm 😌'),
        ('romantic', 'Romantic 💕'),
        ('angry', 'Angry 😠'),
        ('nostalgic', 'Nostalgic 🌅'),
        ('motivated', 'Motivated 💪'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    daily_usage_count = models.IntegerField(default=0)
    last_usage_date = models.DateField(null=True, blank=True)
    current_mood = models.CharField(max_length=20, choices=MOOD_CHOICES, blank=True)
    last_mood_update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - Profile"

    def reset_daily_usage_if_needed(self):
        """Reset usage count if it's a new day"""
        today = timezone.now().date()
        if self.last_usage_date != today:
            self.daily_usage_count = 0
            self.last_usage_date = today
            self.save()

    def increment_usage(self):
        """Increment daily usage count"""
        self.reset_daily_usage_if_needed()
        self.daily_usage_count += 1
        self.save()

    def can_use_service(self, free_limit=10):
        """Check if user can use the service based on subscription or free tier"""
        self.reset_daily_usage_if_needed()

        # Check if user has active subscription
        if self.has_active_subscription():
            return True

        # Check free tier limit
        return self.daily_usage_count < free_limit

    def has_active_subscription(self):
        """Check if user has an active subscription"""
        return self.user.subscriptions.filter(active=True, end_date__gte=timezone.now()).exists()

    def update_mood(self, mood):
        """Update user's current mood"""
        self.current_mood = mood
        self.last_mood_update = timezone.now()
        self.save()


class Subscription(models.Model):
    PLAN_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=False)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    order_id = models.CharField(max_length=255, blank=True)  # For webhook lookup
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.plan_type} - {'Active' if self.active else 'Inactive'}"

    def activate(self):
        """Activate subscription and set dates"""
        self.active = True
        self.start_date = timezone.now()

        if self.plan_type == 'monthly':
            self.end_date = self.start_date + timedelta(days=30)
        elif self.plan_type == 'yearly':
            self.end_date = self.start_date + timedelta(days=365)

        self.save()


class Purchase(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    plan_type = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    order_id = models.CharField(max_length=255, blank=True)  # For webhook lookup
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.plan_type} - ${self.amount} - {self.status}"
