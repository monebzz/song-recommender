import requests
import hashlib
import hmac
from textblob import TextBlob
from django.conf import settings


class DeezerAPI:
    """Wrapper for Deezer API"""
    BASE_URL = "https://api.deezer.com"

    @staticmethod
    def search_songs(query, limit=20):
        """Search for songs on Deezer"""
        try:
            response = requests.get(
                f"{DeezerAPI.BASE_URL}/search",
                params={"q": query, "limit": limit}
            )
            response.raise_for_status()
            data = response.json()
            return data.get('data', [])
        except requests.RequestException as e:
            print(f"Deezer API error: {e}")
            return []

    @staticmethod
    def get_song_details(deezer_id):
        """Get detailed information about a song"""
        try:
            response = requests.get(f"{DeezerAPI.BASE_URL}/track/{deezer_id}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Deezer API error: {e}")
            return None

    @staticmethod
    def get_artist_top_tracks(artist_id, limit=10):
        """Get top tracks for an artist"""
        try:
            response = requests.get(
                f"{DeezerAPI.BASE_URL}/artist/{artist_id}/top",
                params={"limit": limit}
            )
            response.raise_for_status()
            data = response.json()
            return data.get('data', [])
        except requests.RequestException as e:
            print(f"Deezer API error: {e}")
            return []


class SentimentAnalyzer:
    """Analyze sentiment of song titles and lyrics"""

    @staticmethod
    def analyze_text(text):
        """
        Analyze sentiment of text using TextBlob
        Returns a polarity score between -1 (negative) and 1 (positive)
        """
        if not text:
            return 0.0
        
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return 0.0

    @staticmethod
    def analyze_song(title, artist=""):
        """Analyze sentiment of a song based on title and artist"""
        combined_text = f"{title} {artist}"
        return SentimentAnalyzer.analyze_text(combined_text)

    @staticmethod
    def get_sentiment_label(score):
        """Convert sentiment score to human-readable label"""
        if score > 0.3:
            return "Positive"
        elif score < -0.3:
            return "Negative"
        else:
            return "Neutral"


import stripe
from django.conf import settings

class StripeAPI:
    """Wrapper for Stripe payment API"""

    @staticmethod
    def create_checkout_session(amount, plan_type, user_email, order_id):
        """
        Create a Stripe checkout session
        """
        print(f"\n=== STRIPE API: create_checkout_session ===")
        print(f"Amount: {amount}, Plan: {plan_type}, Email: {user_email}, Order ID: {order_id}")

        # Check if Stripe key is set
        stripe_key = settings.STRIPE_SECRET_KEY
        print(f"STRIPE_SECRET_KEY from settings: {stripe_key[:20] if stripe_key else 'NOT SET'}...")
        print(f"SITE_URL from settings: {settings.SITE_URL}")

        if not stripe_key or stripe_key == 'sk_test_your_key':
            print(f"❌ ERROR: Stripe key is not properly configured!")
            return None

        stripe.api_key = stripe_key
        print(f"✅ Stripe API key set")

        try:
            print(f"Creating Stripe checkout session...")
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'{plan_type.title()} Subscription',
                            'description': f'Access to unlimited song recommendations for {plan_type} plan',
                        },
                        'unit_amount': int(amount * 100),  # Convert to cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                customer_email=user_email,
                success_url=f"{settings.SITE_URL}/checkout/success/?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.SITE_URL}/checkout/cancel/",
                metadata={
                    'order_id': order_id,
                    'plan_type': plan_type,
                }
            )

            print(f"✅ Stripe session created successfully: {session.id}")
            print(f"Checkout URL: {session.url[:50]}...")

            return {
                "checkout_url": session.url,
                "session_id": session.id,
                "payment_intent_id": session.payment_intent,
                "status": "pending"
            }
        except Exception as e:
            print(f"❌ Stripe checkout session creation error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def verify_webhook_signature(payload, signature):
        """
        Verify Stripe webhook signature
        """
        try:
            stripe.Webhook.construct_event(
                payload,
                signature,
                settings.STRIPE_WEBHOOK_SECRET
            )
            return True
        except ValueError as e:
            # Invalid payload
            print(f"Webhook signature verification failed: {e}")
            return False
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            print(f"Webhook signature verification failed: {e}")
            return False

    @staticmethod
    def get_payment_status(payment_intent_id):
        """
        Get payment status from Stripe
        """
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                "payment_intent_id": payment_intent.id,
                "status": payment_intent.status,
                "amount": payment_intent.amount / 100,  # Convert from cents
                "currency": payment_intent.currency,
            }
        except Exception as e:
            print(f"Stripe payment status retrieval error: {e}")
            return None


def get_song_recommendations(song, limit=10):
    """
    Get song recommendations based on a given song
    Uses artist's top tracks as recommendations
    """
    from .models import Song
    
    # Try to get recommendations from the same artist
    recommendations = []
    
    # Get song details from Deezer
    song_data = DeezerAPI.get_song_details(song.deezer_id)
    
    if song_data and 'artist' in song_data:
        artist_id = song_data['artist']['id']
        artist_tracks = DeezerAPI.get_artist_top_tracks(artist_id, limit=limit)
        
        for track in artist_tracks:
            # Skip the current song
            if str(track['id']) == song.deezer_id:
                continue
            
            # Get or create song in database
            song_obj, created = Song.objects.get_or_create(
                deezer_id=str(track['id']),
                defaults={
                    'title': track.get('title', ''),
                    'artist': track.get('artist', {}).get('name', ''),
                    'album': track.get('album', {}).get('title', ''),
                    'link': track.get('link', ''),
                    'preview': track.get('preview', ''),
                    'cover': track.get('album', {}).get('cover_medium', ''),
                }
            )
            
            # Calculate sentiment if not already done
            if song_obj.sentiment is None:
                song_obj.sentiment = SentimentAnalyzer.analyze_song(
                    song_obj.title,
                    song_obj.artist
                )
                song_obj.save()
            
            recommendations.append(song_obj)
            
            if len(recommendations) >= limit:
                break
    
    return recommendations


def analyze_mood_text(text):
    """
    Analyze user's mood text input and detect the mood.
    Uses TextBlob sentiment analysis and keyword matching.
    """
    from textblob import TextBlob

    text_lower = text.lower()

    # Keyword-based mood detection
    mood_keywords = {
        'happy': ['happy', 'joyful', 'excited', 'great', 'wonderful', 'amazing', 'fantastic', 'cheerful', 'delighted', 'glad'],
        'sad': ['sad', 'depressed', 'down', 'unhappy', 'miserable', 'heartbroken', 'lonely', 'blue', 'melancholy', 'upset'],
        'energetic': ['energetic', 'pumped', 'hyped', 'active', 'energized', 'powerful', 'dynamic', 'vigorous'],
        'calm': ['calm', 'peaceful', 'relaxed', 'chill', 'tranquil', 'serene', 'mellow', 'zen', 'quiet'],
        'romantic': ['romantic', 'love', 'loving', 'affectionate', 'tender', 'passionate', 'in love', 'smitten'],
        'angry': ['angry', 'mad', 'furious', 'annoyed', 'irritated', 'frustrated', 'rage', 'pissed'],
        'nostalgic': ['nostalgic', 'reminiscing', 'memories', 'remember', 'past', 'old times', 'throwback'],
        'motivated': ['motivated', 'determined', 'focused', 'driven', 'ambitious', 'inspired', 'ready', 'pumped up'],
    }

    # Check for keyword matches
    for mood, keywords in mood_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return mood

    # If no keyword match, use sentiment analysis
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity

    # Map sentiment to mood
    if sentiment > 0.5:
        return 'happy'
    elif sentiment > 0.3:
        return 'calm'
    elif sentiment > 0:
        return 'romantic'
    elif sentiment > -0.3:
        return 'nostalgic'
    elif sentiment > -0.5:
        return 'sad'
    else:
        return 'angry'


def get_mood_based_recommendations(mood, limit=20):
    """
    Get song recommendations based on user's mood.
    Maps mood to sentiment range and returns matching songs from database.
    """
    from .models import Song

    # Map moods to sentiment ranges
    mood_sentiment_map = {
        'happy': (0.3, 1.0),        # Positive songs
        'sad': (-1.0, -0.2),        # Negative songs
        'energetic': (0.4, 1.0),    # Very positive songs
        'calm': (-0.1, 0.3),        # Neutral to slightly positive
        'romantic': (0.2, 0.7),     # Moderately positive
        'angry': (-1.0, -0.3),      # Negative songs
        'nostalgic': (-0.2, 0.2),   # Neutral songs
        'motivated': (0.5, 1.0),    # Very positive songs
    }

    # Get sentiment range for the mood
    sentiment_range = mood_sentiment_map.get(mood, (-1.0, 1.0))
    min_sentiment, max_sentiment = sentiment_range

    # Query songs within the sentiment range
    songs = Song.objects.filter(
        sentiment__gte=min_sentiment,
        sentiment__lte=max_sentiment,
        sentiment__isnull=False
    ).order_by('?')[:limit]  # Random order

    return list(songs)

