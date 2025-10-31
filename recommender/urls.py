from django.urls import path
from . import views

urlpatterns = [
    # Web views
    path('', views.home, name='home'),

    # Authentication
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),

    # Main features
    path('recommendations/', views.mood_recommendations, name='mood_recommendations'),
    path('search/', views.search_songs, name='search'),
    path('song/<str:deezer_id>/', views.song_detail, name='song_detail'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('subscribe/<str:plan_type>/', views.subscribe, name='subscribe_plan'),
    # Specific checkout routes MUST come before generic <str:plan_type> route
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    path('checkout/cancel/', views.checkout_cancel, name='checkout_cancel'),
    path('checkout/<str:plan_type>/', views.checkout, name='checkout'),

    # Webhook
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    
    # API endpoints
    path('api/search/', views.api_search_songs, name='api_search'),
    path('api/song/<str:deezer_id>/', views.api_song_detail, name='api_song_detail'),
    path('api/recommend/<str:deezer_id>/', views.api_recommend, name='api_recommend'),
    path('api/checkout/', views.api_checkout, name='api_checkout'),
    path('api/create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
]

