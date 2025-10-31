from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Song, UserProfile, Subscription, Purchase
from .utils import SentimentAnalyzer


class SongModelTest(TestCase):
    def setUp(self):
        self.song = Song.objects.create(
            deezer_id='12345',
            title='Happy Song',
            artist='Test Artist',
            album='Test Album',
            link='https://deezer.com/track/12345',
            preview='https://deezer.com/preview/12345',
            sentiment=0.8
        )

    def test_song_creation(self):
        self.assertEqual(self.song.title, 'Happy Song')
        self.assertEqual(self.song.artist, 'Test Artist')
        self.assertEqual(self.song.sentiment, 0.8)

    def test_song_str(self):
        self.assertEqual(str(self.song), 'Happy Song - Test Artist')


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            daily_usage_count=0
        )

    def test_profile_creation(self):
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.daily_usage_count, 0)

    def test_increment_usage(self):
        self.profile.increment_usage()
        self.assertEqual(self.profile.daily_usage_count, 1)
        self.assertEqual(self.profile.last_usage_date, timezone.now().date())

    def test_reset_daily_usage(self):
        self.profile.daily_usage_count = 5
        self.profile.last_usage_date = timezone.now().date() - timedelta(days=1)
        self.profile.save()

        self.profile.reset_daily_usage_if_needed()
        self.assertEqual(self.profile.daily_usage_count, 0)

    def test_can_use_service_free_tier(self):
        self.profile.daily_usage_count = 5
        self.profile.last_usage_date = timezone.now().date()
        self.profile.save()

        self.assertTrue(self.profile.can_use_service(free_limit=10))

        self.profile.daily_usage_count = 10
        self.profile.save()

        self.assertFalse(self.profile.can_use_service(free_limit=10))

    def test_can_use_service_with_subscription(self):
        # Create active subscription
        subscription = Subscription.objects.create(
            user=self.user,
            plan_type='monthly',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            active=True
        )

        self.profile.daily_usage_count = 100
        self.profile.save()

        # Should still be able to use service with subscription
        self.assertTrue(self.profile.can_use_service(free_limit=10))


class SubscriptionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_subscription_creation(self):
        subscription = Subscription.objects.create(
            user=self.user,
            plan_type='monthly',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            active=True
        )

        self.assertEqual(subscription.plan_type, 'monthly')
        self.assertTrue(subscription.active)

    def test_subscription_activation(self):
        subscription = Subscription.objects.create(
            user=self.user,
            plan_type='monthly',
            active=False
        )

        subscription.activate()

        self.assertTrue(subscription.active)
        self.assertIsNotNone(subscription.start_date)
        self.assertIsNotNone(subscription.end_date)

    def test_yearly_subscription_duration(self):
        subscription = Subscription.objects.create(
            user=self.user,
            plan_type='yearly',
            active=False
        )

        subscription.activate()

        duration = (subscription.end_date - subscription.start_date).days
        self.assertEqual(duration, 365)


class PurchaseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_purchase_creation(self):
        purchase = Purchase.objects.create(
            user=self.user,
            plan_type='monthly',
            amount=20.00,
            status='pending',
            safepay_order_id='order_123'
        )

        self.assertEqual(purchase.amount, 20.00)
        self.assertEqual(purchase.status, 'pending')


class SentimentAnalyzerTest(TestCase):
    def test_positive_sentiment(self):
        score = SentimentAnalyzer.analyze_text('I love this amazing wonderful song')
        self.assertGreater(score, 0)

    def test_negative_sentiment(self):
        score = SentimentAnalyzer.analyze_text('I hate this terrible awful song')
        self.assertLess(score, 0)

    def test_neutral_sentiment(self):
        score = SentimentAnalyzer.analyze_text('This is a song')
        self.assertAlmostEqual(score, 0, delta=0.3)

    def test_sentiment_label(self):
        self.assertEqual(SentimentAnalyzer.get_sentiment_label(0.5), 'Positive')
        self.assertEqual(SentimentAnalyzer.get_sentiment_label(-0.5), 'Negative')
        self.assertEqual(SentimentAnalyzer.get_sentiment_label(0.0), 'Neutral')


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Song Recommender')

    def test_search_requires_login(self):
        response = self.client.get('/search/?q=test')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_subscribe_page_requires_login(self):
        response = self.client.get('/subscribe/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_subscribe_page_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/subscribe/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Monthly Plan')
        self.assertContains(response, 'Yearly Plan')
