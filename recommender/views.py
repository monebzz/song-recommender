from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
import json
import uuid
import stripe
from django.core.mail import send_mail
from django.urls import reverse

from .models import Song, UserProfile, Subscription, Purchase
from .serializers import (
    SongSerializer, UserProfileSerializer,
    SubscriptionSerializer, PurchaseSerializer, CheckoutSerializer
)
from .utils import DeezerAPI, SentimentAnalyzer, StripeAPI, get_song_recommendations, get_mood_based_recommendations


# Web Views

def home(request):
    """Home page - Ask user how they're feeling"""
    if not request.user.is_authenticated:
        return render(request, 'recommender/home.html', {'show_auth': True})

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Handle mood text input
    if request.method == 'POST':
        mood_text = request.POST.get('mood_text', '').strip()
        if mood_text:
            # Check if user can use the service
            if not profile.can_use_service():
                messages.error(
                    request,
                    f'You have reached your daily limit of {settings.FREE_USAGE_LIMIT} recommendations. '
                    'Please subscribe for unlimited access.'
                )
                return redirect('subscribe')

            # Analyze the mood text to detect sentiment
            from .utils import analyze_mood_text
            detected_mood = analyze_mood_text(mood_text)

            # Update user's mood
            profile.update_mood(detected_mood)
            # Store the original text
            request.session['mood_text'] = mood_text
            # Redirect to recommendations
            return redirect('mood_recommendations')

    context = {
        'profile': profile,
        'can_use': profile.can_use_service(),
        'usage_count': profile.daily_usage_count,
        'free_limit': settings.FREE_USAGE_LIMIT,
    }
    return render(request, 'recommender/home.html', context)


def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'recommender/login.html')


def user_signup(request):
    """User signup view"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validation
        if not username or not password1 or not email:
            messages.error(request, 'Username, email, and password are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            # Create user
            user = User.objects.create_user(username=username, email=email, password=password1)
            
            # Create profile with verification token
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Send verification email
            verification_url = request.build_absolute_uri(
                reverse('verify_email', args=[profile.verification_token])
            )
            
            subject = 'Verify your email address'
            message = f'Hi {user.username},\n\nPlease click the link below to verify your email address:\n\n{verification_url}\n\nThanks,\nSong Recommender Team'
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, f'Account created! Please check your email ({email}) to verify your account.')
            except Exception as e:
                import traceback
                print(f"❌ Error sending email: {e}")
                print(f"Full traceback:")
                traceback.print_exc()
                print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
                print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
                print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
                print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
                print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
                messages.warning(request, 'Account created but failed to send verification email.')

            login(request, user)
            return redirect('home')

    return render(request, 'recommender/signup.html')


def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def verify_email(request, token):
    """Verify user's email address"""
    try:
        profile = UserProfile.objects.get(verification_token=token)
        if not profile.email_verified:
            profile.email_verified = True
            profile.save()
            messages.success(request, 'Your email has been verified successfully!')
        else:
            messages.info(request, 'Your email is already verified.')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
    
    return redirect('home')


@login_required
def mood_recommendations(request):
    """Show song recommendations based on user's mood"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Check if user has selected a mood
    if not profile.current_mood:
        messages.warning(request, 'Please tell us how you\'re feeling first.')
        return redirect('home')

    # Increment usage count
    profile.increment_usage()

    # Get mood-based recommendations
    recommendations = get_mood_based_recommendations(profile.current_mood, limit=20)

    # If no songs in database, show message
    if not recommendations:
        messages.info(
            request,
            'No songs found for your mood yet. Please ask admin to seed the database with songs.'
        )

    # Get the original mood text from session
    mood_text = request.session.get('mood_text', '')

    context = {
        'profile': profile,
        'mood': profile.current_mood,
        'mood_text': mood_text,
        'mood_display': dict(UserProfile.MOOD_CHOICES).get(profile.current_mood, profile.current_mood.title()),
        'recommendations': recommendations,
        'usage_count': profile.daily_usage_count,
        'free_limit': settings.FREE_USAGE_LIMIT,
        'can_use': profile.can_use_service(),
    }
    return render(request, 'recommender/mood_recommendations.html', context)


@login_required
def search_songs(request):
    """Search songs and display results"""
    query = request.GET.get('q', '')

    if not query:
        messages.warning(request, 'Please enter a search query.')
        return redirect('home')

    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Check if user can use the service
    free_limit = getattr(settings, 'FREE_USAGE_LIMIT', 10)

    if not profile.can_use_service(free_limit):
        messages.error(
            request,
            f'You have reached your daily limit of {free_limit} searches. '
            'Please subscribe for unlimited access.'
        )
        return redirect('subscribe')

    # Increment usage
    profile.increment_usage()

    # Search songs via Deezer API
    results = DeezerAPI.search_songs(query)

    # Store songs in database and calculate sentiment
    songs = []
    for track in results:
        preview = track.get('preview', '')
        cover = track.get('album', {}).get('cover_medium', '')
        # Skip songs without preview or cover
        if not preview or not cover:
            continue

        song, created = Song.objects.get_or_create(
            deezer_id=str(track['id']),
            defaults={
                'title': track.get('title', ''),
                'artist': track.get('artist', {}).get('name', ''),
                'album': track.get('album', {}).get('title', ''),
                'link': track.get('link', ''),
                'preview': preview,
                'cover': cover,
            }
        )

        # Calculate sentiment if not already done
        if song.sentiment is None:
            song.sentiment = SentimentAnalyzer.analyze_song(song.title, song.artist)
            song.save()

        songs.append(song)

    context = {
        'query': query, 
        'songs': songs,
        'usage_count': profile.daily_usage_count,
        'usage_limit': free_limit,
        'has_subscription': profile.has_active_subscription(),
    }

    return render(request, 'recommender/search_results.html', context)


@login_required
def song_detail(request, deezer_id):
    """Display song details and recommendations"""
    song = get_object_or_404(Song, deezer_id=deezer_id)

    # Get recommendations
    recommendations = get_song_recommendations(song, limit=10)

    # Get sentiment label
    sentiment_label = SentimentAnalyzer.get_sentiment_label(song.sentiment or 0)

    context = {
        'song': song,
        'recommendations': recommendations,
        'sentiment_label': sentiment_label,
    }

    return render(request, 'recommender/song_detail.html', context)


@login_required
def subscribe(request, plan_type=None):
    """Display subscription plans"""
    monthly_price = getattr(settings, 'MONTHLY_PLAN_PRICE', 20)
    yearly_price = getattr(settings, 'YEARLY_PLAN_PRICE', 100)

    # Get user's active subscription if any
    profile = UserProfile.objects.get_or_create(user=request.user)[0]
    active_subscription = request.user.subscriptions.filter(active=True).first()

    # If plan_type is provided, redirect to checkout
    if plan_type in ['monthly', 'yearly']:
        return redirect('checkout', plan_type=plan_type)

    context = {
        'monthly_price': monthly_price,
        'yearly_price': yearly_price,
        'active_subscription': active_subscription,
        'has_subscription': profile.has_active_subscription(),
    }

    return render(request, 'recommender/subscribe.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def create_payment_intent(request):
    """Create a Stripe PaymentIntent for direct payment"""
    try:
        data = json.loads(request.body)
        plan_type = data.get('plan_type')

        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        if plan_type not in ['monthly', 'yearly']:
            return JsonResponse({'error': 'Invalid plan type'}, status=400)

        # Get plan price
        if plan_type == 'monthly':
            amount = getattr(settings, 'MONTHLY_PLAN_PRICE', 20)
        else:
            amount = getattr(settings, 'YEARLY_PLAN_PRICE', 100)

        # Create purchase and subscription records
        order_id = str(uuid.uuid4())

        purchase = Purchase.objects.create(
            user=request.user,
            plan_type=plan_type,
            amount=amount,
            status='pending',
            stripe_payment_intent_id=order_id,
            order_id=order_id
        )

        subscription = Subscription.objects.create(
            user=request.user,
            plan_type=plan_type,
            stripe_payment_intent_id=order_id,
            order_id=order_id,
            active=False
        )

        # Create Stripe PaymentIntent
        stripe.api_key = settings.STRIPE_SECRET_KEY
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency='usd',
            automatic_payment_methods={
                'enabled': True,
                'allow_redirects': 'never'
            },
            description=f'{plan_type.title()} Subscription - Song Recommender',
            metadata={
                'order_id': order_id,
                'plan_type': plan_type,
                'user_id': request.user.id,
            }
        )

        # Update records with actual payment intent ID
        purchase.stripe_payment_intent_id = intent.id
        purchase.save()
        subscription.stripe_payment_intent_id = intent.id
        subscription.save()

        return JsonResponse({
            'client_secret': intent.client_secret,
            'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            'amount': amount,
            'plan_type': plan_type,
        })

    except Exception as e:
        print(f"Error creating payment intent: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def checkout(request, plan_type):
    """Show checkout page with Stripe payment form"""
    if plan_type not in ['monthly', 'yearly']:
        messages.error(request, 'Invalid plan type.')
        return redirect('subscribe')

    # Get plan price
    if plan_type == 'monthly':
        amount = getattr(settings, 'MONTHLY_PLAN_PRICE', 20)
    else:
        amount = getattr(settings, 'YEARLY_PLAN_PRICE', 100)

    try:
        # Create purchase and subscription records
        order_id = str(uuid.uuid4())

        purchase = Purchase.objects.create(
            user=request.user,
            plan_type=plan_type,
            amount=amount,
            status='pending',
            stripe_payment_intent_id=order_id,
            order_id=order_id
        )

        subscription = Subscription.objects.create(
            user=request.user,
            plan_type=plan_type,
            stripe_payment_intent_id=order_id,
            order_id=order_id,
            active=False
        )

        # Create Stripe PaymentIntent
        stripe.api_key = settings.STRIPE_SECRET_KEY
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency='usd',
            automatic_payment_methods={
                'enabled': True,
                'allow_redirects': 'never'
            },
            description=f'{plan_type.title()} Subscription - Song Recommender',
            metadata={
                'order_id': order_id,
                'plan_type': plan_type,
                'user_id': request.user.id,
            }
        )

        # Update records with actual payment intent ID
        purchase.stripe_payment_intent_id = intent.id
        purchase.save()
        subscription.stripe_payment_intent_id = intent.id
        subscription.save()

        context = {
            'client_secret': intent.client_secret,
            'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            'amount': amount,
            'plan_type': plan_type,
            'order_id': order_id,
        }

        return render(request, 'recommender/checkout.html', context)

    except Exception as e:
        print(f"❌ ERROR in checkout view: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, f'Error: {str(e)}')
        return redirect('subscribe')


@login_required
def checkout_success(request):
    """Handle successful Stripe payment"""
    session_id = request.GET.get('session_id')

    if not session_id:
        messages.error(request, 'Invalid session.')
        return redirect('subscribe')

    try:
        # Get the subscription that was just activated
        subscription = Subscription.objects.filter(
            user=request.user,
            active=True
        ).latest('created_at')

        context = {
            'subscription': subscription,
            'plan_type': subscription.plan_type,
            'end_date': subscription.end_date,
        }

        return render(request, 'recommender/checkout_success.html', context)
    except Subscription.DoesNotExist:
        messages.warning(request, 'Payment received. Your subscription will be activated shortly.')
        return redirect('home')


@login_required
def checkout_cancel(request):
    """Handle cancelled Stripe payment"""
    messages.info(request, 'Payment cancelled. No charges were made.')
    return redirect('subscribe')


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Handle Stripe webhook for payment confirmation"""
    try:
        # Get webhook signature from headers
        signature = request.headers.get('stripe-signature', '')

        # Get payload
        payload = request.body.decode('utf-8')

        # Verify signature
        if not StripeAPI.verify_webhook_signature(payload, signature):
            print("❌ Webhook signature verification failed")
            return HttpResponse(status=401)

        # Parse webhook data
        data = json.loads(payload)

        event_type = data.get('type')
        event_data = data.get('data', {}).get('object', {})

        print(f"📨 Webhook received: {event_type}")

        if event_type == 'checkout.session.completed':
            # Checkout session completed successfully
            session_id = event_data.get('id')
            payment_intent_id = event_data.get('payment_intent')
            metadata = event_data.get('metadata', {})
            order_id = metadata.get('order_id')

            print(f"✅ Checkout session completed: {session_id}, payment_intent: {payment_intent_id}, order_id: {order_id}")

            # Find purchase and subscription by order_id
            try:
                if order_id:
                    purchase = Purchase.objects.get(order_id=order_id)
                    subscription = Subscription.objects.get(order_id=order_id)

                    # Update purchase
                    purchase.stripe_payment_intent_id = payment_intent_id
                    purchase.status = 'completed'
                    purchase.save()
                    print(f"✅ Purchase {purchase.id} marked as completed")

                    # Activate subscription
                    subscription.stripe_payment_intent_id = payment_intent_id
                    subscription.activate()
                    print(f"✅ Subscription {subscription.id} activated for user {subscription.user.username}")

                    return HttpResponse(status=200)
                else:
                    print("❌ No order_id found in checkout session metadata")
                    return HttpResponse(status=404)

            except (Purchase.DoesNotExist, Subscription.DoesNotExist) as e:
                print(f"❌ Purchase or subscription not found for order_id: {order_id}")
                print(f"Error: {e}")
                return HttpResponse(status=404)

        elif event_type == 'payment_intent.payment_failed':
            # Payment failed
            payment_intent_id = event_data.get('id')

            try:
                purchase = Purchase.objects.get(stripe_payment_intent_id=payment_intent_id)
                purchase.status = 'failed'
                purchase.save()
            except Purchase.DoesNotExist:
                print(f"Purchase not found for failed payment_intent_id: {payment_intent_id}")

        return HttpResponse(status=200)

    except Exception as e:
        print(f"Webhook error: {e}")
        return HttpResponse(status=500)


# API Views

@api_view(['GET'])
def api_search_songs(request):
    """API endpoint for searching songs"""
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    query = request.GET.get('q', '')

    if not query:
        return Response(
            {'error': 'Query parameter "q" is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Check if user can use the service
    free_limit = getattr(settings, 'FREE_USAGE_LIMIT', 10)

    if not profile.can_use_service(free_limit):
        return Response(
            {
                'error': f'Daily limit of {free_limit} searches reached. Please subscribe.',
                'usage_count': profile.daily_usage_count,
                'limit': free_limit,
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    # Increment usage
    profile.increment_usage()

    # Search songs via Deezer API
    results = DeezerAPI.search_songs(query)

    # Store songs in database and calculate sentiment
    songs = []
    for track in results:
        preview = track.get('preview', '')
        cover = track.get('album', {}).get('cover_medium', '')
        # Skip songs without preview or cover
        if not preview or not cover:
            continue

        song, created = Song.objects.get_or_create(
            deezer_id=str(track['id']),
            defaults={
                'title': track.get('title', ''),
                'artist': track.get('artist', {}).get('name', ''),
                'album': track.get('album', {}).get('title', ''),
                'link': track.get('link', ''),
                'preview': preview,
                'cover': cover,
            }
        )

        # Calculate sentiment if not already done
        if song.sentiment is None:
            song.sentiment = SentimentAnalyzer.analyze_song(song.title, song.artist)
            song.save()

        songs.append(song)

    serializer = SongSerializer(songs, many=True)

    return Response({
        'query': query,
        'results': serializer.data,
        'usage_count': profile.daily_usage_count,
        'usage_limit': free_limit,
        'has_subscription': profile.has_active_subscription(),
    })


@api_view(['GET'])
def api_song_detail(request, deezer_id):
    """API endpoint for song details"""
    try:
        song = Song.objects.get(deezer_id=deezer_id)
    except Song.DoesNotExist:
        return Response(
            {'error': 'Song not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = SongSerializer(song)
    return Response(serializer.data)


@api_view(['GET'])
def api_recommend(request, deezer_id):
    """API endpoint for song recommendations"""
    try:
        song = Song.objects.get(deezer_id=deezer_id)
    except Song.DoesNotExist:
        return Response(
            {'error': 'Song not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    recommendations = get_song_recommendations(song, limit=10)
    serializer = SongSerializer(recommendations, many=True)

    return Response({
        'song': SongSerializer(song).data,
        'recommendations': serializer.data,
    })


@api_view(['POST'])
def api_checkout(request):
    """API endpoint for creating checkout session"""
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    serializer = CheckoutSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    plan_type = serializer.validated_data['plan_type']

    # Get plan price
    if plan_type == 'monthly':
        amount = getattr(settings, 'MONTHLY_PLAN_PRICE', 20)
    else:
        amount = getattr(settings, 'YEARLY_PLAN_PRICE', 100)

    # Create purchase record
    order_id = str(uuid.uuid4())
    purchase = Purchase.objects.create(
        user=request.user,
        plan_type=plan_type,
        amount=amount,
        status='pending',
        stripe_payment_intent_id=order_id,
        order_id=order_id
    )

    # Create subscription record (inactive until payment confirmed)
    subscription = Subscription.objects.create(
        user=request.user,
        plan_type=plan_type,
        stripe_payment_intent_id=order_id,
        order_id=order_id,
        active=False
    )

    # Create Stripe checkout session
    checkout_data = StripeAPI.create_checkout_session(
        amount=amount,
        plan_type=plan_type,
        user_email=request.user.email,
        order_id=order_id
    )

    if not checkout_data:
        return Response(
            {'error': 'Failed to create checkout session'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Update purchase and subscription with actual Stripe payment_intent_id
    actual_payment_intent_id = checkout_data.get('payment_intent_id')
    if actual_payment_intent_id:
        purchase.stripe_payment_intent_id = actual_payment_intent_id
        purchase.save()
        subscription.stripe_payment_intent_id = actual_payment_intent_id
        subscription.save()

    return Response({
        'checkout_url': checkout_data.get('checkout_url'),
        'order_id': order_id,
        'amount': amount,
        'plan_type': plan_type,
    })
