import os
import json
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv

class SpotifyAPI():
    def __init__(self):
       self.access_token = self.get_access_token()
    
    def create_env_file(self, client_id, client_secret):
        """Create .env file with credentials"""
        env_content = f"""SPOTIFY_CLIENT_ID={client_id}
                    SPOTIFY_CLIENT_SECRET={client_secret}
                    SPOTIFY_REDIRECT_URI={self.redirect_uri}
                    """

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

    def authorize(self):
        pass

    def get_access_token(self):
        """Get access token via authentification or authorization"""

        if os.path.exists("spotify_credentials"):
            return self.authenticate()
        else:
            return self.authorize()

    def get_playlist(self):
        pass

class MusicDownloader:
    
    def __init__(self, extra=None, dest_file=None):
        # load previous configurations
        self.load_confi(dest_file=dest_file)
        # change wdir to target directory and store dir
        self.target_folder = self.set_wdir(extra=extra)
        # get access tocken for interacting with spotify
        self.access_token = self.get_access_token()

    def get_music_path(self, extra=None):
        """Detect OS and on that basic get dir for music"""
        home = Path.home()
        music_dir = home / "Music"

        # return music directory or music subfolder
        if music_dir.exists():
            # go one level deeper 
            if extra:
                music_dir = music_dir / extra
                return music_dir
            else:
                return music_dir 
        # return desktop 
        return home / "Desktop"
                
    
    def load_confi(self, dest_file=None):
        """Load configurations"""

        if os.path.exists("configurarions.json"):
            with open("confgurations.json", "r") as fhand:
                    self.state = json.load(fhand)
                    
                    # change target folder
                    if dest_file:
                        self.state["local_file"] = dest_file
                        json.dump(self.state, fhand)
        # initialize configurations
        else:
            self.state = {"local_folder": dest_file}
            # save configuration
            with open("configurarions.json", "w") as fhand:
                json.dump(self.state, fhand)
    
    def set_wdir(self, extra=None):
        """Set working directory to target directory"""
        # create target directory and change directory 
        target_dir = self.get_music_path(extra=extra) + self.state["local_folder"]
        os.chdir(target_dir)

        return target_dir

    def get_local_songs(self):
        """Extract local songs"""

        self.local_songs = []

        # iterate over local files 
        for file in Path(".").iterdir():
            if file.is_file():
                # extract song name and added it to local files
                self.local_songs.append(file.name.split(".")[0])

        
    def get_songs_list(self, spotify_plist) -> list:
        """
        Find the songs that are in the Spotify playlist but not
        in the local file. This are the songs to be downloaded.
        """


    def edit_song_metadata():
        """Edit the song Meta data to correclty"""
        pass

class Tester():
    def __inti__(self):
        self.mdownloader = MusicDownloader()
        self.s_api = SpotifyAPI()
        self.dummy_conf 

    def md_setup(self):
        """Test if initial setup is done correctly"""
        music_dir = self.mdownloader.get_music_path()
        print(f"The music path in computer is: {music_dir}")


    def md_songs_to_download(self):
        pass

    def md_download_song(self):
        pass

    def md_song_metadata(self):
        pass


def main():
    mdownloader = MusicDownloader()

    test = Tester()


if __name__ == "__main__":
    main()
    

    