# 🚀 Quick Start Guide

Get the Mood-Based Song Recommender running in 5 minutes!

## Prerequisites
- Python 3.8+ installed
- pip package manager

## Step-by-Step Setup

### 1️⃣ Install Dependencies (1 minute)
```bash
pip install -r requirements.txt
```

### 2️⃣ Setup Environment (30 seconds)
```bash
# Copy environment template
cp .env.example .env

# The default values work fine for local development
# Edit .env only if you have real Safepay API keys
```

### 3️⃣ Initialize Database (1 minute)
```bash
# Run migrations
python manage.py migrate

# Create admin and test users
python create_test_user.py
```

**Created Users:**
- Admin: `admin` / `admin123`
- Test User: `testuser` / `test123`

### 4️⃣ Seed Sample Data (1 minute)
```bash
# Add 40 songs across all moods to the database
python seed_mock_songs.py
```

This adds songs for all 8 moods:
- Happy songs (e.g., "Happy" by Pharrell Williams)
- Sad songs (e.g., "Someone Like You" by Adele)
- Energetic songs (e.g., "Eye of the Tiger")
- Calm songs (e.g., "Weightless" by Marconi Union)
- Romantic songs (e.g., "Perfect" by Ed Sheeran)
- Angry songs (e.g., "Break Stuff" by Limp Bizkit)
- Nostalgic songs (e.g., "Yesterday" by The Beatles)
- Motivated songs (e.g., "Lose Yourself" by Eminem)

### 5️⃣ Start the Server (10 seconds)
```bash
python manage.py runserver
```

### 6️⃣ Open Your Browser
Visit: **http://127.0.0.1:8000**

---

## 🎯 What to Try

### As a Regular User
1. Go to http://127.0.0.1:8000
2. Login with `testuser` / `test123`
3. **Select your mood** - Click on one of the 8 mood buttons (😊 Happy, 😢 Sad, ⚡ Energetic, etc.)
4. **View recommendations** - See songs that match your emotional state
5. **Listen to previews** - Use the audio player to hear song snippets
6. **Try different moods** - Go back and select another mood
7. **Hit the limit** - Try 10+ recommendations to see the free tier limit
8. **View subscription plans** - See upgrade options for unlimited access

### As an Admin
1. Go to http://127.0.0.1:8000/admin/
2. Login with `admin` / `admin123`
3. Browse Songs, User Profiles, Subscriptions, Purchases
4. Create/edit records

### API Testing
```bash
# Search songs (requires authentication)
curl -u testuser:test123 "http://127.0.0.1:8000/api/search/?q=love"

# Get song details
curl "http://127.0.0.1:8000/api/song/3135556/"

# Get recommendations
curl "http://127.0.0.1:8000/api/recommend/3135556/"
```

---

## 🧪 Run Tests
```bash
python manage.py test recommender
```

Expected: **19 tests passing** ✅

---

## 📱 Features to Explore

✅ **Mood Selection** - Choose from 8 different moods (Happy, Sad, Energetic, Calm, Romantic, Angry, Nostalgic, Motivated)
✅ **Sentiment Analysis** - Songs are analyzed to determine their emotional tone
✅ **Smart Matching** - AI matches your mood with song sentiment scores
✅ **Personalized Recommendations** - Get songs that match how you're feeling
✅ **Free Tier** - 10 recommendations per day for free users
✅ **Subscriptions** - Monthly ($20) and Yearly ($100) plans for unlimited access
✅ **Audio Previews** - Listen to 30-second previews
✅ **REST API** - Full API access with DRF

---

## 🔧 Troubleshooting

### "No module named 'textblob'"
```bash
pip install textblob
python -m textblob.download_corpora
```

### "No module named 'dotenv'"
```bash
pip install python-dotenv
```

### Database issues
```bash
# Delete and recreate database
rm db.sqlite3
python manage.py migrate
python create_test_user.py
```

### Port already in use
```bash
# Use a different port
python manage.py runserver 8001
```

---

## 📚 Documentation

- **README.md** - Full setup guide
- **PROJECT_SUMMARY.md** - Complete project documentation
- **requirements.txt** - All dependencies
- **.env.example** - Configuration template

---

## 🎉 You're Ready!

The application is now running at **http://127.0.0.1:8000**

Enjoy exploring the Song Recommender! 🎵

