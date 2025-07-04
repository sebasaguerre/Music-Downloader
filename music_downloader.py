import os
import sys 
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
        self.load_config(dest_file=dest_file)
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
                
    
    def load_config(self, config_file="conjugurations.json", dest_file=None):
        """setup or load configutation file"""

        if os.path.exists(config_file):
            with open(config_file, "r") as fhand:
                    self.state = json.load(fhand)
                    
                    # change target folder
                    if dest_file:
                        self.state["local_file"] = dest_file
                        json.dump(self.state, fhand)
        # initialize configurations
        else:
            self.state = {"local_folder": dest_file}
            # save configuration
            with open(config_file, "w") as fhand:
                json.dump(self.state, fhand)
    
    def set_wdir(self, extra=None):
        """Set working directory to target directory"""
        # create target directory and change directory 
        target_dir = self.get_music_path(extra=extra) + self.state["local_folder"]
        
        # check if subfolder exists else create it
        if not os.path.exists(target_dir):
            try:
                os.mkdir(target_dir)
            except Exception as e:
                sys.exit(f"Error {e} while creating target directory...")
        
        # change wdir to target_dir
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
        self.mdownload = MusicDownloader()
        self.s_api = SpotifyAPI()
        self.dummy_conf 

    def md_setup(self):
        """Test if initial setup is done correctly"""

        # create configuration file 
        self.mdownload.load_config(config_file="dummy.json", dest_file="dummy_file1")
        if os.path.exists("dummy.jason"):
            print("Configuration file created succesfully!")
        else:
            print("No configuratrion file has been created...")
            return 1

        # load configuration file and change destination folder
        self.mdownload.load_config(config_file="dummy.json", dest_file="dummy_file2")
        if self.mdownload.state["local_file"] == "dummy_file2":
            print("Destination folder update correctly!")
        else:
            print("Destination folder not updated...")
            return 2
        # remove configuration file 
        os.remove("dummy.json")

        # check music directory and set directory 
        prog_dir = Path.cwd()
        print(f"Music directory: {self.mdownload.get_music_path()}")
        print(f"Destination dir. {self.mdownload.target_folder}")

        if self.mdownload.target_folder == Path.cwd():
            print("Working directory changed succesfuly!")
            # change back to original dir and remove dummy folder
            os.chdir(prog_dir)
            os.rmdir(self.mdownload.target_folder)
        
        else:
            print("Working directory not changed")
            return 3

        print("\nSet-up test PASSED!")

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
    

    