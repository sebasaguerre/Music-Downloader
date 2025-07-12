import sys
import os
import time
import base64
import requests
import threading
import webbrowser
from dotenv import load_dotenv
from pathlib import Path
import urllib.parse as url_parse
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler

class CallbackHandler:
    def __init__(self):
        pass

class SpotifyOAuth():
    def __init__(self):
        """Initialize with app credentials"""
        self.env_file = Path(".env")
        self.redirect_url = "http://localhost:8080/callback"
        self.self.load_credentials()
        self.access_token = self.get_access_token()

    def load_credentials(self):
        """
        Load user data from .env into instance variables
        or create .env file 
        """

        if self.env_file.exist():
            load_dotenv()
            self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
            self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
            self.access_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
            self.refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
            self.expires_at = os.getenv("EXPIRATION_DATE")

            if not self.client_id or not self.client_secret:
                raise Exception("No SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET in .env file")

        else:
            raise Exception("No .env file found")
    
    def create_env_file(self, client_id, client_secret, access_token=None, refresh_token=None):
        """Create .env file with credentials"""

        # initial env content set up 
        env_content = f"""SPOTIFY_CLIENT_ID={client_id}
                    SPOTIFY_CLIENT_SECRET={client_secret}
                    SPOTIFY_REDIRECT_URI={self.redirect_uri}
                    """
        
        if access_token:
            env_content += f"SPOTIFY_ACCESS_TOKEN={access_token}"
        if refresh_token:
            env_content += f"SPOTIFY_REDIRECT_URI={refresh_token}"

        # write down content to .env file 
        self.env_file.write_text(env_content)

        # load enviorment 
        self.load_credentials()

    def setup_oauth_flow(self):
        """Setup Oauth flow if credentials don't exist"""
        # give instructions to users to get credentials 
        print("""Setting up Spotify OAuth...
              1. Go to https://developer.spotify.com/dashboard and login
              2. Create an app or select existing app
              3. Copy your Client ID and Client Secret 
              """)
        
        client_id = input("\nEnter your Client ID: ").strip()
        client_secret = input("\nEnter your Client Secret: ").strip()

        # create .env file 
        self.create_env_file(client_id, client_secret)

        # start OAuth process 
        self.user_authorization()

    def build_auth_url(self):
        """Build Spotify authorization URL"""
        base_url = "https://accounts.spotify.com/authorize"
        scope = "user-read-private playlist-read-private playlist-read-collaborative"

        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_url": self.redirect_url,
            "scope": scope,
            "show_dialog": True 
        }

        return f"{base_url}?{params}"
    
    def code_for_token(self, auth_code):
        """Exchange authorizatrion code for access token"""
        url = "https://accounts.spotify.com/api/token"

        # create basic auth header (app authentficatrion)
        credentials = f"{self.client_id}:{self.client_secret}"
        credentials_b64 = base64.b64code(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {credentials_b64}",
            "Content-type": "application/x-www-form-urlencoded"
        }

        data = {
            "Authorization": "authorization_code",
            "code": auth_code,
            "redirect_url": self.redirect_url
        }

        # make request 
        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Token exchange failed: {response.text}")

    def user_authorization(self):
        """Get user authorization for playlist access"""

        # generate authorization URL 
        auth_url = self.build_auth_url()

        # start local server to catch callback 
        server = HTTPServer(("localhost", 8080), CallbackHandler)
        server.auth_code = None

        # run server in background 
        # create seperate thread to run server 
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True  # kill thread when server is shutdown 
        server_thread.start()
        
        # open browser for user authorization
        webbrowser.open(auth_url)

        # wait to receive authorizatoin code
        while server.auth_code is None:
            time.sleep(1)

        # extract code and  shutdown server
        auth_code = server.auth_code
        server.shutdown()

        # exchange code for tokens and save tokens to .env
        tokens = self.exchange_code_for_tokens(auth_code)
        self.save_tokens_to_env(tokens)

        return tokens
    
    def save_token_to_env(self, tokens):
        """Save new tokens into .env file for future usage"""

        existing_content = "" 
        if self.env_file.exists():
            existing_content = self.env_file.read_test()
        
        # update or add tokens
        updated_lines = []
        added_access = False
        added_refresh = False

        for line in existing_content.split("\n"):
            # check for access token
            if line.startswith("SPOTIFY_ACCESS_TOKEN="):
                updated_lines.append(line)
                added_access = True
            # check for refresh toek
            elif line.startswith("SPOTIFY_REFRESH_TOKEN="):
                updated_lines.append(line)
                added_refresh = True
            else:
                updated_lines.append(line)
        
        # add new lines if not found 
        if not added_access:
            updated_lines.append(f"SPOTIFY_ACCESS_TOKEN={tokens["access_token"]}")
        if not added_refresh:
            updated_lines.append(f"SPOTIFY_REFRESH_TOKEN={tokens["refresh_token"]}")

        # add expiration time for access token 
        expires_at = datetime.now().timestamp() + tokens["expires_in"]
        updated_lines.append(f"EXPIATION_DATE={expires_at}")
        
        # write tokens in .env file
        self.env_file.write_text("\n".join(updated_lines))

        # update instance variables
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]

    def get_access_token(self):
        """
        Get access token if it has not yet expired or get a new one
        via the refresh token.
        """
        
        # if access token expires, get new one
        if datetime.now().timestamp() > self.expires_at:
            # if no refresh token go through authorization process
            if not self.refresh_token():
                return self.user_authorization()
            # refresh access token 
            url = "https://account.spotify.com/api/token"

            credentials = f"{self.client_id}:{self.client_secret}"
            credential_b64 = base64.b64encode(credentials.encode()).decode()
            
        else:
            return self.access_token

    def authenticate(self):
        """Authenticate with Spotify API and get access token"""
        # load credentials
        load_dotenv()
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secrete = os.getenv("SPOTIFY_CLIENT_SECRET")
        credentials = f"{client_id}:{client_secrete}"
        # convert to b64
        cred_b64 = base64.b64encode(credentials.encode()).decode()

        # headers for request 
        header = {
            "Authorization": f"Basic {cred_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        # api requirements 
        url = "https://accounts.spotify.com/api/token"
        data = {"grant_type": "client_credentials"}

        respose = requests.post(url, headers=header, data=data)
        return respose.json()


    def get_access_token(self):
        """Get access token via authentification or authorization"""

        if os.path.exists("spotify_credentials"):
            return self.authenticate()
        else:
            return self.authorize()


class SpotifyAPI:
    def __init__(self):
        self.auth = SpotifyOAuth()

    def get_playlist(self):
        pass