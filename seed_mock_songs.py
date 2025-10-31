import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'song_recommender.settings')
django.setup()

from recommender.models import Song
from recommender.utils import SentimentAnalyzer

# Mock songs with different sentiments
mock_songs = [
    # Happy songs (positive sentiment)
    {"deezer_id": "1001", "title": "Happy", "artist": "Pharrell Williams", "album": "G I R L", "link": "https://www.deezer.com/track/1001", "preview": ""},
    {"deezer_id": "1002", "title": "Good Vibrations", "artist": "The Beach Boys", "album": "Smiley Smile", "link": "https://www.deezer.com/track/1002", "preview": ""},
    {"deezer_id": "1003", "title": "Walking on Sunshine", "artist": "Katrina and the Waves", "album": "Walking on Sunshine", "link": "https://www.deezer.com/track/1003", "preview": ""},
    {"deezer_id": "1004", "title": "Don't Stop Me Now", "artist": "Queen", "album": "Jazz", "link": "https://www.deezer.com/track/1004", "preview": ""},
    {"deezer_id": "1005", "title": "I Gotta Feeling", "artist": "The Black Eyed Peas", "album": "The E.N.D.", "link": "https://www.deezer.com/track/1005", "preview": ""},
    
    # Sad songs (negative sentiment)
    {"deezer_id": "2001", "title": "Someone Like You", "artist": "Adele", "album": "21", "link": "https://www.deezer.com/track/2001", "preview": ""},
    {"deezer_id": "2002", "title": "Tears in Heaven", "artist": "Eric Clapton", "album": "Unplugged", "link": "https://www.deezer.com/track/2002", "preview": ""},
    {"deezer_id": "2003", "title": "Hurt", "artist": "Johnny Cash", "album": "American IV", "link": "https://www.deezer.com/track/2003", "preview": ""},
    {"deezer_id": "2004", "title": "Mad World", "artist": "Gary Jules", "album": "Trading Snakeoil for Wolftickets", "link": "https://www.deezer.com/track/2004", "preview": ""},
    {"deezer_id": "2005", "title": "The Sound of Silence", "artist": "Simon & Garfunkel", "album": "Sounds of Silence", "link": "https://www.deezer.com/track/2005", "preview": ""},
    
    # Energetic songs (very positive)
    {"deezer_id": "3001", "title": "Eye of the Tiger", "artist": "Survivor", "album": "Eye of the Tiger", "link": "https://www.deezer.com/track/3001", "preview": ""},
    {"deezer_id": "3002", "title": "Thunderstruck", "artist": "AC/DC", "album": "The Razors Edge", "link": "https://www.deezer.com/track/3002", "preview": ""},
    {"deezer_id": "3003", "title": "We Will Rock You", "artist": "Queen", "album": "News of the World", "link": "https://www.deezer.com/track/3003", "preview": ""},
    {"deezer_id": "3004", "title": "Pump It", "artist": "The Black Eyed Peas", "album": "Monkey Business", "link": "https://www.deezer.com/track/3004", "preview": ""},
    {"deezer_id": "3005", "title": "Can't Hold Us", "artist": "Macklemore & Ryan Lewis", "album": "The Heist", "link": "https://www.deezer.com/track/3005", "preview": ""},
    
    # Calm songs (neutral to slightly positive)
    {"deezer_id": "4001", "title": "Weightless", "artist": "Marconi Union", "album": "Weightless", "link": "https://www.deezer.com/track/4001", "preview": ""},
    {"deezer_id": "4002", "title": "Clair de Lune", "artist": "Claude Debussy", "album": "Suite bergamasque", "link": "https://www.deezer.com/track/4002", "preview": ""},
    {"deezer_id": "4003", "title": "Breathe", "artist": "Pink Floyd", "album": "The Dark Side of the Moon", "link": "https://www.deezer.com/track/4003", "preview": ""},
    {"deezer_id": "4004", "title": "Sunset Lover", "artist": "Petit Biscuit", "album": "Petit Biscuit", "link": "https://www.deezer.com/track/4004", "preview": ""},
    {"deezer_id": "4005", "title": "River Flows in You", "artist": "Yiruma", "album": "First Love", "link": "https://www.deezer.com/track/4005", "preview": ""},
    
    # Romantic songs (moderately positive)
    {"deezer_id": "5001", "title": "Perfect", "artist": "Ed Sheeran", "album": "÷", "link": "https://www.deezer.com/track/5001", "preview": ""},
    {"deezer_id": "5002", "title": "Thinking Out Loud", "artist": "Ed Sheeran", "album": "x", "link": "https://www.deezer.com/track/5002", "preview": ""},
    {"deezer_id": "5003", "title": "All of Me", "artist": "John Legend", "album": "Love in the Future", "link": "https://www.deezer.com/track/5003", "preview": ""},
    {"deezer_id": "5004", "title": "Make You Feel My Love", "artist": "Adele", "album": "19", "link": "https://www.deezer.com/track/5004", "preview": ""},
    {"deezer_id": "5005", "title": "A Thousand Years", "artist": "Christina Perri", "album": "The Twilight Saga", "link": "https://www.deezer.com/track/5005", "preview": ""},
    
    # Angry songs (negative)
    {"deezer_id": "6001", "title": "Break Stuff", "artist": "Limp Bizkit", "album": "Significant Other", "link": "https://www.deezer.com/track/6001", "preview": ""},
    {"deezer_id": "6002", "title": "Killing in the Name", "artist": "Rage Against the Machine", "album": "Rage Against the Machine", "link": "https://www.deezer.com/track/6002", "preview": ""},
    {"deezer_id": "6003", "title": "Bodies", "artist": "Drowning Pool", "album": "Sinner", "link": "https://www.deezer.com/track/6003", "preview": ""},
    {"deezer_id": "6004", "title": "Chop Suey!", "artist": "System of a Down", "album": "Toxicity", "link": "https://www.deezer.com/track/6004", "preview": ""},
    {"deezer_id": "6005", "title": "Last Resort", "artist": "Papa Roach", "album": "Infest", "link": "https://www.deezer.com/track/6005", "preview": ""},
    
    # Nostalgic songs (neutral)
    {"deezer_id": "7001", "title": "Yesterday", "artist": "The Beatles", "album": "Help!", "link": "https://www.deezer.com/track/7001", "preview": ""},
    {"deezer_id": "7002", "title": "Wonderwall", "artist": "Oasis", "album": "(What's the Story) Morning Glory?", "link": "https://www.deezer.com/track/7002", "preview": ""},
    {"deezer_id": "7003", "title": "Bohemian Rhapsody", "artist": "Queen", "album": "A Night at the Opera", "link": "https://www.deezer.com/track/7003", "preview": ""},
    {"deezer_id": "7004", "title": "Hotel California", "artist": "Eagles", "album": "Hotel California", "link": "https://www.deezer.com/track/7004", "preview": ""},
    {"deezer_id": "7005", "title": "Sweet Child O' Mine", "artist": "Guns N' Roses", "album": "Appetite for Destruction", "link": "https://www.deezer.com/track/7005", "preview": ""},
    
    # Motivated songs (very positive)
    {"deezer_id": "8001", "title": "Stronger", "artist": "Kanye West", "album": "Graduation", "link": "https://www.deezer.com/track/8001", "preview": ""},
    {"deezer_id": "8002", "title": "Lose Yourself", "artist": "Eminem", "album": "8 Mile Soundtrack", "link": "https://www.deezer.com/track/8002", "preview": ""},
    {"deezer_id": "8003", "title": "Hall of Fame", "artist": "The Script ft. will.i.am", "album": "#3", "link": "https://www.deezer.com/track/8003", "preview": ""},
    {"deezer_id": "8004", "title": "Roar", "artist": "Katy Perry", "album": "Prism", "link": "https://www.deezer.com/track/8004", "preview": ""},
    {"deezer_id": "8005", "title": "Fight Song", "artist": "Rachel Platten", "album": "Wildfire", "link": "https://www.deezer.com/track/8005", "preview": ""},
]

analyzer = SentimentAnalyzer()
created_count = 0
updated_count = 0

for song_data in mock_songs:
    # Calculate sentiment
    sentiment = analyzer.analyze_song(song_data['title'], song_data['artist'])
    song_data['sentiment'] = sentiment
    
    # Create or update song
    song, created = Song.objects.update_or_create(
        deezer_id=song_data['deezer_id'],
        defaults=song_data
    )
    
    if created:
        created_count += 1
        print(f"✅ Created: {song.title} by {song.artist} (sentiment: {sentiment:.2f})")
    else:
        updated_count += 1
        print(f"🔄 Updated: {song.title} by {song.artist} (sentiment: {sentiment:.2f})")

print(f"\n🎉 Done! Created {created_count} songs, updated {updated_count} songs.")
print(f"Total songs in database: {Song.objects.count()}")

