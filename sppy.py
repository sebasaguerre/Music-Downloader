import spotipy
from spotipy.oauth2 import SpotifyOAuth

# This handles ALL the OAuth complexity for you
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="http://localhost:8080/callback",
    scope="playlist-modify-public user-read-private"
))

# Now you can directly use Spotify API
user_info = sp.current_user()
playlists = sp.current_user_playlists()