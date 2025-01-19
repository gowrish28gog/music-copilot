import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class LyricsFetcher:
    def __init__(self, spotify_client_id, spotify_client_secret, genius_access_token):
        """
        Initialize with both Spotify and Genius credentials
        """
        self.genius_token = genius_access_token
        # Initialize Spotify client
        self.spotify_client = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=spotify_client_id,
                client_secret=spotify_client_secret
            )
        )
        
    def get_spotify_track_info(self, spotify_url):
        """
        Get track information from Spotify URL
        """
        try:
            # Extract track ID from URL
            track_id = spotify_url.split('/')[-1].split('?')[0]
            
            # Get track information
            track_info = self.spotify_client.track(track_id)
            
            return {
                'name': track_info['name'],
                'artist': track_info['artists'][0]['name'],
                'album': track_info['album']['name'],
                'release_date': track_info['album']['release_date']
            }
        except Exception as e:
            raise Exception(f"Error fetching Spotify track info: {str(e)}")

    def search_genius(self, track_name, artist_name):
        """
        Search for a song on Genius
        """
        base_url = "https://api.genius.com"
        headers = {'Authorization': f'Bearer {self.genius_token}'}
        search_url = f"{base_url}/search"
        
        try:
            response = requests.get(
                search_url,
                params={'q': f"{track_name} {artist_name}"},
                headers=headers
            )
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            raise Exception(f"Error searching Genius: {str(e)}")

    def extract_lyrics_from_genius(self, genius_url):
        """
        Extract lyrics from Genius webpage
        """
        try:
            # Add headers to mimic browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(genius_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try different possible lyrics containers
            lyrics_div = soup.find('div', class_='lyrics')
            if not lyrics_div:
                lyrics_div = soup.find('div', class_='Lyrics__Container-sc-1ynbvzw-6')
            if not lyrics_div:
                # Find all lyric containers if the above methods fail
                lyrics_divs = soup.find_all('div', {'data-lyrics-container': 'true'})
                if lyrics_divs:
                    lyrics = '\n'.join([div.get_text() for div in lyrics_divs])
                    return lyrics
            
            if lyrics_div:
                lyrics = lyrics_div.get_text()
                # Clean up lyrics
                return '\n'.join(line.strip() for line in lyrics.split('\n') if line.strip())
            
            return None
        except Exception as e:
            raise Exception(f"Error extracting lyrics: {str(e)}")

    def get_lyrics(self, spotify_url):
        """
        Main method to get lyrics from Spotify URL
        """
        try:
            # Get track info from Spotify
            track_info = self.get_spotify_track_info(spotify_url)
            
            # Search for the song on Genius
            genius_response = self.search_genius(
                track_info['name'],
                track_info['artist']
            )
            
            # Process Genius response
            if 'response' in genius_response and genius_response['response']['hits']:
                song_info = genius_response['response']['hits'][0]['result']
                
                # Get lyrics from Genius page
                lyrics = self.extract_lyrics_from_genius(song_info['url'])
                
                return {
                    'status': 'success',
                    'spotify_info': track_info,
                    'genius_info': {
                        'title': song_info['title'],
                        'artist': song_info['primary_artist']['name'],
                        'genius_url': song_info['url']
                    },
                    'lyrics': lyrics if lyrics else 'Lyrics not found'
                }
            
            return {
                'status': 'error',
                'message': 'Song not found on Genius'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

def main():
    """
    Test the lyrics fetcher
    """
    # Replace these with your actual API credentials  
    SPOTIFY_CLIENT_ID = ""
    SPOTIFY_CLIENT_SECRET = ""
    GENIUS_ACCESS_TOKEN = ""  # Replace with your actual token
    
    
    # Initialize the fetcher
    fetcher = LyricsFetcher(
        spotify_client_id=SPOTIFY_CLIENT_ID,
        spotify_client_secret=SPOTIFY_CLIENT_SECRET,
        genius_access_token=GENIUS_ACCESS_TOKEN
    )
    
    # Test with a real Spotify URL
    spotify_url = "https://open.spotify.com/track/3E5WzHizGIGTfO2a2guWV0?si=1e0fedb4fb9249f0"  # Shape of You
    
    print("Fetching lyrics...")
    result = fetcher.get_lyrics(spotify_url)
    
    if result['status'] == 'success':
        print("\nSpotify Track Information:")
        print(f"Track: {result['spotify_info']['name']}")
        print(f"Artist: {result['spotify_info']['artist']}")
        print(f"Album: {result['spotify_info']['album']}")
        print(f"Release Date: {result['spotify_info']['release_date']}")
        
        print("\nGenius Information:")
        print(f"Genius Title: {result['genius_info']['title']}")
        print(f"Genius Artist: {result['genius_info']['artist']}")
        print(f"Genius URL: {result['genius_info']['genius_url']}")
        
        print("\nLyrics:")
        print("----------------------------------------")
        print(result['lyrics'])
        print("----------------------------------------")
    else:
        print(f"Error: {result['message']}")

if __name__ == "__main__":
    main()
