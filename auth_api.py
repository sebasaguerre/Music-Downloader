import sys
import os
import time
import base64
import requests
import tempfile
import threading
import webbrowser
from dotenv import load_dotenv, set_key
from pathlib import Path
import urllib.parse as url_parse
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler

class CallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback"""
    def do_GET(self):
        # parse the authorization code from the callback url
        if "code=" in self.path:
            # extract code from callback url
            # callback url path example: "GET /callback?code=ABC123&state=xyz HTTP/1.1"
            code = self.path.split("code=")[1].split("&")[0]

            # store code in server instance 
            self.server.auth_code = code

            # send HTTP response back to browser
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            # html response with JavaScript to cose browser automatically
            html_autoclose_response = """
            <html>
            <head><title>Authorization Successful</title></head>
            <body>
                <h1>Authorization completed successfully!</h1>
                <p>This window will close automatically in 2 seconds...</p>
                <script>
                    setTimeout(function() {
                        window.close();
                    }, 2000);
                </script>
            </body>
            </html>
            """
            html_standard_response = b"""
            <html>
                <head><title>Success</title><head>
                <body>
                    <h1>Successful authorization! You can close this window.</h1>
                </body>
            </html>
            """
            self.wfile.write(html_autoclose_response.encode())

        # error handeling
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Error in authorization</h1>")
    
    def log_message(self, format, *args):
        pass # suppress server log 

class SpotifyOAuth():
    def __init__(self, test=False):
        """Initialize with app credentials"""

        self.redirect_url = "http://127.0.0.1:8000/callback"
        self.test = test

        # set OAuth  based on test 
        if not self.test:
            self.env_file = Path(".env")
            self.load_credentials()
            self.access_token = self.get_access_token()
        else:
            # set ddummy path to manualy to create .env
            # and proccede with authentificaiton 
            self.env_file = Path("dummy.env")
        
    def load_credentials(self):
        """
        Load user data from .env into instance variables
        or create .env file 
        """

        if self.env_file.exists():
            load_dotenv()
            self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
            self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
            self.access_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
            self.refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
            self.expires_at = os.getenv("EXPIRATION_DATE")
            # convert expiration time to float
            if self.expires_at:
                self.expires_at = float(self.expires_at)

            if not self.client_id or not self.client_secret:
                raise Exception("No SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET in .env file")

        else:
            raise Exception("No .env file found")
            # for future create enviorment by pulling info from server
            self.create_env_file()
    
    def create_env_file(self, client_id, client_secret, access_token=None, refresh_token=None):
        """Create .env file with credentials"""

        # initial env content 
        set_key(self.env_file, "SPOTIFY_CLIENT_ID", client_id)
        set_key(self.env_file, "SPOTIFY_CLIENT_SECRET", client_secret)

        if access_token:
            set_key(self.env_file, "SPOTIFY_ACCESS_TOKEN", access_token)
        if refresh_token:
            set_key(self.env_file, "SPOTIFY_REFRESH_TOKEN", refresh_token)

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
            "redirect_uri": self.redirect_url,
            "scope": scope,
            "show_dialog": True 
        }

        # oparser encoder converts the parameters into urls encoded format
        return f"{base_url}?{url_parse.urlencode(params)}"
    
    def code_for_token(self, auth_code):
        """
        Exchange authorizatrion code for access token using
        Basic Authentification:
            Authentification: Basic base64encode('client_id:client_secret')
        """
        url = "https://accounts.spotify.com/api/token"
        

        # create basic auth header (app authentficatrion)
        credentials = f"{self.client_id}:{self.client_secret}"
        credentials_b64 = base64.b64encode(credentials.encode()).decode()

        # meta data 
        headers = {
            "Authorization": f"Basic {credentials_b64}",
            "Content-type": "application/x-www-form-urlencoded" # tells server the format of the data
        }

        # actual contentn being send to API
        data = {
            "grant_type": "authorization_code", # what do we want to do 
            "code": auth_code,
            "redirect_uri": self.redirect_url
        }

        # make request 
        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Token exchange failed: {response.text}")

    def user_authorization(self, popup=False):
        """Get user authorization for playlist access"""

        # generate authorization URL 
        auth_url = self.build_auth_url()

        # start local server to catch callback 
        server = HTTPServer(("localhost", 8000), CallbackHandler)
        server.auth_code = None

        # run server in background 
        # create seperate thread to run server 
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True  # kill thread when server is shutdown 
        server_thread.start()
        
        # open browser or popup for authorization
        if not popup:
            webbrowser.open(auth_url)
        else:
            # open html file and repplace placeholder
            with open("spotify_auth.html", "r") as fhand:
                html = fhand.read()
            html = html.replace("AUTH_URL_PLACEHOLDER", auth_url)

            # create temporal file 
            with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as fhand:
                fhand.write(html)
                temp_file = fhand.name 
            
            # open temporary file
            webbrowser.open(f"file://{temp_file}")

        # wait to receive authorizatoin code
        while server.auth_code is None:
            time.sleep(1)

        # extract code and  shutdown server
        auth_code = server.auth_code
        server.shutdown()

        # clean-up temporary file if popup was used
        if popup:
            os.unlink(temp_file)

        # exchange code for tokens and save tokens to .env
        tokens = self.code_for_token(auth_code)
        if self.test: print("Tokens retrieved!\nSaving tokens...")
        self.save_tokens_to_env(tokens)

        return tokens
    
    def save_tokens_to_env(self, tokens):
        """Save new tokens into .env file for future usage"""
        expires_at = datetime.now().timestamp() + tokens["expires_in"]

        # update enviroment variables
        set_key(self.env_file, "SPOTIFY_ACCESS_TOKEN", tokens["access_token"])
        set_key(self.env_file, "SPOTIFY_REFRESH_TOKEN", tokens["refresh_token"])
        set_key(self.env_file, "EXPIRATION_DATE", str(expires_at))

        # update instance variables
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]
        self.expires_at = expires_at

    
    # def save_tokens_to_env(self, tokens):
    #     """Save new tokens into .env file for future usage"""

    #     existing_content = "" 
    #     if self.env_file.exists():
    #         existing_content = self.env_file.read_text()
        
    #     # update or add tokens
    #     updated_lines = []
    #     added_access = False
    #     added_refresh = False
    #     added_expiration = False

    #     # update tokens if they aready existed in the enviorment file 
    #     for line in existing_content.split("\n"):
    #         # check for access token
    #         if line.startswith(f"SPOTIFY_ACCESS_TOKEN="):
    #             updated_lines.append(f"SPOTIFY_ACCESS_TOKEN={tokens["access_token"]}")
    #             added_access = True
    #         # check for refresh token
    #         elif line.startswith("SPOTIFY_REFRESH_TOKEN="):
    #             updated_lines.append(f"SPOTIFY_REFRESH_TOKEN={tokens["refresh_token"]}")
    #             added_refresh = True
    #         # check if expiration date exists
    #         elif line.startswith("EXPIRATION_DATE="):
    #             expires_at = datetime.now().timestamp() + tokens["expires_in"]
    #             updated_lines.append(f"EXPIRATION_DATE={expires_at}")
    #             added_expiration = True 
    #         else:
    #             updated_lines.append(line)
        
    #     # add new lines if not found 
    #     if not added_access:
    #         updated_lines.append(f"SPOTIFY_ACCESS_TOKEN={tokens['access_token']}")
    #     if not added_refresh:
    #         updated_lines.append(f"SPOTIFY_REFRESH_TOKEN={tokens['refresh_token']}")
    #     if not added_expiration:
    #         # add expiration time for access token 
    #         expires_at = datetime.now().timestamp() + tokens["expires in"]
    #         updated_lines.append(f"EXPIRES_IN={expires_at}")

    #     # write tokens in .env file
    #     self.env_file.write_text("\n".join(updated_lines))

    #     # update instance variables
    #     self.access_token = tokens["access_token"]
    #     self.refresh_token = tokens["refresh_token"]
    #     self.expires_at = expires_at

    def get_access_token(self):
        """
        Get access token if it has not yet expired or get a new one
        via the refresh token.
        """
        # if we have accesstoken and it is not expired use it 
        if self.access_token and self.expires_at and datetime.now().timestamp() < float(self.expires_at):
            return self.access_token
        # if expired and we have refresh token, refresh access token
        elif self.refresh_token:
            return self.refresh_access_token()
        # else authentificate 
        else: 
            return self.user_authorization()

    def refresh_access_token(self):
        """Refresh accesstoken using refresh token"""
        # refresh access token 
        url = "https://account.spotify.com/api/token"

        credentials = f"{self.client_id}:{self.client_secret}"
        credentials_b64 = base64.b64encode(credentials.encode()).decode()

        # headers and data for request.post 
        headers = {
            "Authorization": f"Basic {credentials_b64}",
            "Content-Type": "application/x-www-forom-utlencoded"
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            tokens = response.json()
            self.save_token_to_env(tokens)
            return self.access_token
        else:
            print("Token refresh failed. Starting new authorization flow...")
            return self.user_authorization()


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


    # def get_access_token(self):
    #     """Get access token via authentification or authorization"""

    #     if os.path.exists("spotify_credentials"):
    #         return self.authenticate()
    #     else:
    #         return self.authorize()


class SpotifyAPI:
    def __init__(self):
        pass
        # self.auth = SpotifyOAuth()

    def get_playlist(self):
        pass