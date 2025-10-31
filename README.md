# 🎵 Song Recommender - Mood-Based Music Discovery

A Django-based mood-driven song recommendation system that asks users how they're feeling and recommends songs that match their emotional state using AI-powered sentiment analysis.

## 🎯 How It Works

1. **User logs in** to the application
2. **Selects their current mood** from 8 options (Happy, Sad, Energetic, Calm, Romantic, Angry, Nostalgic, Motivated)
3. **System analyzes songs** in the database using TextBlob sentiment analysis
4. **Receives personalized recommendations** - songs that match their emotional state
5. **Listens and enjoys** music that resonates with how they feel

## ✨ Features

### Core Functionality
- 😊 **Mood-Based Recommendations**: Select from 8 different moods
- 🎭 **Sentiment Analysis**: TextBlob-powered emotional analysis of songs
- 🎵 **Smart Matching**: AI matches your mood with song sentiment scores
- 🎧 **Audio Previews**: Listen to 30-second previews (when available)
- 📊 **Sentiment Scores**: See the emotional tone of each song

### Business Model
- 🆓 **Free Tier**: 10 recommendations per day
- 💎 **Premium Plans**: 
  - Monthly: $20/month for unlimited recommendations
  - Yearly: $100/year for unlimited recommendations
- 💳 **Safepay Integration**: Secure payment processing
- 🔔 **Webhook Support**: Automatic subscription activation

### Technical Features
- 🌐 **Web Interface**: Beautiful Bootstrap 5 responsive UI
- 🔌 **REST API**: Full DRF-powered API endpoints
- 🔐 **Authentication**: Django's built-in auth system
- 📱 **Mobile-Friendly**: Responsive design works on all devices
- 🎨 **Modern UI**: Clean, intuitive interface with mood emojis

## 🎭 Available Moods

| Mood | Emoji | Sentiment Range | Example Songs |
|------|-------|-----------------|---------------|
| Happy | 😊 | 0.3 to 1.0 | "Happy" by Pharrell Williams |
| Sad | 😢 | -1.0 to -0.2 | "Someone Like You" by Adele |
| Energetic | ⚡ | 0.4 to 1.0 | "Eye of the Tiger" by Survivor |
| Calm | 😌 | -0.1 to 0.3 | "Weightless" by Marconi Union |
| Romantic | 💕 | 0.2 to 0.7 | "Perfect" by Ed Sheeran |
| Angry | 😠 | -1.0 to -0.3 | "Break Stuff" by Limp Bizkit |
| Nostalgic | 🌅 | -0.2 to 0.2 | "Yesterday" by The Beatles |
| Motivated | 💪 | 0.5 to 1.0 | "Lose Yourself" by Eminem |

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup environment
cp .env.example .env
# Edit .env if you have Safepay API keys

# 3. Run migrations
python manage.py migrate

# 4. Create users
python create_test_user.py
# Creates: admin/admin123 and testuser/test123

# 5. Seed database with songs
python seed_mock_songs.py
# Adds 40 songs across all moods

# 6. Start server
python manage.py runserver
```

### Access the Application
- **Web App**: http://127.0.0.1:8000
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Login**: testuser / test123
- **Admin**: admin / admin123

## 📖 User Guide

### For Regular Users

1. **Login** at http://127.0.0.1:8000
2. **Select your mood** by clicking one of the 8 mood buttons
3. **View recommendations** - songs that match your emotional state
4. **Listen to previews** using the built-in audio player
5. **View details** to see more about each song
6. **Try different moods** to discover new music

### Free Tier Limits
- 10 recommendations per day
- Resets at midnight (UTC)
- Counter shows remaining recommendations
- Upgrade prompt when limit reached

### Subscription Benefits
- **Unlimited recommendations** per day
- **No waiting** - instant access anytime
- **Premium badge** on your profile
- **Monthly or yearly** billing options

## 🔧 Configuration

### Environment Variables (.env)

```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

# Safepay Configuration
SAFEPAY_PUBLIC_KEY=pk_test_your_key
SAFEPAY_SECRET_KEY=sk_test_your_key

# Business Logic
FREE_USAGE_LIMIT=10
MONTHLY_PLAN_PRICE=20
YEARLY_PLAN_PRICE=100
```

## 🗄️ Database Models

### Song
- Stores song information with sentiment scores
- Fields: title, artist, album, deezer_id, sentiment, preview, link

### UserProfile
- Tracks user's mood and daily usage
- Fields: current_mood, daily_usage_count, last_usage_date
- Methods: `update_mood()`, `can_use_service()`, `has_active_subscription()`

### Subscription
- Manages user subscriptions
- Fields: plan_type, start_date, end_date, active, safepay_order_id
- Methods: `activate()`

### Purchase
- Records payment transactions
- Fields: amount, status, plan_type, safepay_order_id

## 🌐 API Endpoints

### Web Views
- `GET /` - Home page with mood selection
- `GET /recommendations/` - View mood-based recommendations
- `GET /song/<deezer_id>/` - Song details
- `GET /subscribe/` - Subscription plans
- `GET /checkout/<plan_type>/` - Checkout page
- `POST /webhook/safepay/` - Payment webhook

### REST API
- `GET /api/search/?q=<query>` - Search songs
- `GET /api/song/<deezer_id>/` - Get song details
- `GET /api/recommend/<deezer_id>/` - Get recommendations
- `POST /api/checkout/` - Create checkout session

## 🧪 Testing

```bash
# Run all tests
python manage.py test recommender

# Expected: 19 tests passing
```

## 📊 Admin Panel

Access at http://127.0.0.1:8000/admin/

### Available Models
- **Songs**: View/edit all songs and their sentiment scores
- **User Profiles**: See user moods and usage statistics
- **Subscriptions**: Manage active subscriptions
- **Purchases**: View payment history

## 💡 How Sentiment Analysis Works

1. **TextBlob Analysis**: Each song's title and artist are analyzed
2. **Polarity Score**: Ranges from -1.0 (negative) to +1.0 (positive)
3. **Mood Mapping**: Each mood maps to a sentiment range
4. **Smart Matching**: System finds songs within the mood's range
5. **Random Selection**: Provides variety in recommendations

### Example Sentiment Scores
- "Happy" by Pharrell Williams: **0.80** (Very Positive)
- "Mad World" by Gary Jules: **-0.62** (Negative)
- "Perfect" by Ed Sheeran: **1.00** (Maximum Positive)
- "Yesterday" by The Beatles: **0.00** (Neutral)

## 🛠️ Management Commands

### Seed Songs from Deezer
```bash
python manage.py seed_songs --q "pop" --limit 50
```

### Seed Mock Songs (Offline)
```bash
python seed_mock_songs.py
```

### Create Test Users
```bash
python create_test_user.py
```

## 📁 Project Structure

```
song_recommender/
├── recommender/              # Main Django app
│   ├── models.py            # Song, UserProfile, Subscription, Purchase
│   ├── views.py             # Web views + API endpoints
│   ├── utils.py             # Sentiment analysis, mood matching
│   ├── templates/           # HTML templates
│   │   ├── home.html        # Mood selection page
│   │   └── mood_recommendations.html  # Results page
│   └── management/commands/
│       └── seed_songs.py    # Database seeding
├── song_recommender/         # Django project settings
│   ├── settings.py          # Configuration
│   └── urls.py              # URL routing
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── seed_mock_songs.py       # Offline song seeding
└── create_test_user.py      # User creation helper
```

## 🎨 UI Screenshots

### Home Page
- Large mood selection buttons with emojis
- Usage counter for free tier
- Clean, modern design

### Recommendations Page
- Song cards with sentiment badges
- Audio preview players
- "Change Mood" button
- Upgrade prompt for free users

## 🔐 Security

- CSRF protection on all forms
- Webhook signature verification
- Environment-based secrets
- Django's built-in auth system
- SQL injection protection via ORM

## 🚀 Deployment

### Production Checklist
1. Set `DEBUG=False` in .env
2. Add your domain to `ALLOWED_HOSTS`
3. Use real Safepay API keys
4. Set up HTTPS (Let's Encrypt)
5. Use PostgreSQL instead of SQLite
6. Configure static files serving
7. Set up email notifications
8. Enable logging

## 📝 License

This project is for educational purposes.

## 🤝 Contributing

This is a demonstration project. Feel free to fork and modify!

## 📞 Support

For issues or questions, please check the documentation or create an issue.

---

**Made with ❤️ using Django, TextBlob, and Bootstrap**

