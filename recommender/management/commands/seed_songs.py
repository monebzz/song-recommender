from django.core.management.base import BaseCommand
from recommender.models import Song
from recommender.utils import DeezerAPI, SentimentAnalyzer


class Command(BaseCommand):
    help = 'Seed the database with songs from Deezer API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--q',
            type=str,
            default='pop',
            help='Search query for songs (default: pop)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Number of songs to fetch (default: 50)'
        )

    def handle(self, *args, **options):
        query = options['q']
        limit = options['limit']

        self.stdout.write(f'Searching for "{query}" songs...')

        # Search songs via Deezer API
        results = DeezerAPI.search_songs(query, limit=limit)

        if not results:
            self.stdout.write(self.style.WARNING('No songs found.'))
            return

        created_count = 0
        updated_count = 0

        for track in results:
            deezer_id = str(track['id'])
            title = track.get('title', '')
            artist = track.get('artist', {}).get('name', '')
            album = track.get('album', {}).get('title', '')
            link = track.get('link', '')
            preview = track.get('preview', '')
            cover = track.get('album', {}).get('cover_medium', '')

            # Skip songs without preview or cover
            if not preview:
                self.stdout.write(
                    self.style.WARNING(f'○ Skipped (no preview): {title} - {artist}')
                )
                continue
            if not cover:
                self.stdout.write(
                    self.style.WARNING(f'○ Skipped (no cover): {title} - {artist}')
                )
                continue

            # Get or create song
            song, created = Song.objects.get_or_create(
                deezer_id=deezer_id,
                defaults={
                    'title': title,
                    'artist': artist,
                    'album': album,
                    'link': link,
                    'preview': preview,
                    'cover': cover,
                }
            )

            # Calculate sentiment if not already done
            if song.sentiment is None:
                song.sentiment = SentimentAnalyzer.analyze_song(title, artist)
                song.save()

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {title} - {artist}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'○ Already exists: {title} - {artist}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Created: {created_count}, Already existed: {updated_count}'
            )
        )

