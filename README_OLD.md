# Song Recommender

A Django-based song recommendation system with sentiment analysis, Deezer API integration, and Safepay payment processing.

## Features

- **Song Search**: Search songs using Deezer API
- **Sentiment Analysis**: Analyze song sentiment using TextBlob
- **Free Tier**: 10 free recommendations per day for non-subscribed users
- **Subscription Plans**: 
  - Monthly: $20/month
  - Yearly: $100/year
- **Payment Integration**: Safepay checkout and webhook handling
- **Web UI**: Bootstrap-based responsive interface
- **REST API**: Full API support with Django REST Framework

## Setup Guide

### 1. Create and activate virtual environment

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your Safepay API keys.

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create superuser (optional)

```bash
python manage.py createsuperuser
```

### 6. Seed initial songs (optional)

```bash
python manage.py seed_songs --q 'pop'
```

### 7. Run development server

```bash
python manage.py runserver
```

Then open http://127.0.0.1:8000

## API Endpoints

- `GET /api/search/?q=<query>` - Search songs
- `GET /api/song/<deezer_id>/` - Get song details
- `GET /api/recommend/<deezer_id>/` - Get recommendations
- `POST /api/checkout/` - Create Safepay checkout session
- `POST /webhook/safepay/` - Safepay webhook handler

## Models

- **Song**: Stores song data from Deezer with sentiment scores
- **UserProfile**: Tracks daily usage for free tier limits
- **Subscription**: Manages user subscription plans
- **Purchase**: Records payment transactions

## Testing

```bash
pytest
```

## License

MIT

