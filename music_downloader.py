import os
import sys 
import json
import argparse
from auth_api import SpotifyOAuth, SpotifyAPI
from pathlib import Path
from dotenv import load_dotenv

class MusicDownloader:
    def __init__(self, test=False, config_file="configuration.json", extra=None, dest_file=None):
        # standard setup when not testing:
        if not test:
            # load previous configurations
            self.load_config(config_file=config_file, dest_file=dest_file)
            # change wdir to target directory and store dir
            self.target_folder = self.set_wdir(extra=extra)

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
            with open(config_file, "r+") as fhand:
                    self.state = json.load(fhand)
                    
            # change target folder and save info
            if dest_file:
                self.state["local_file"] = dest_file
                with open(config_file, "w") as fhand:
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
        target_dir = self.get_music_path(extra=extra) / self.state["local_folder"]
        
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
    def __init__(self):
        # initialize all three classes
        self.mdownload = MusicDownloader(test=True)
        self.api = SpotifyAPI() 
        self.oauth = SpotifyOAuth(test=True)

    def setup(self):
        """Test if initial setup is done correctly"""
        print("Begin setup testing...\n")

        # create configuration file 
        self.mdownload.load_config(config_file="dummy.json", dest_file="dummy_file1")
        if os.path.exists("dummy.json"):
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
        target_dir = self.mdownload.set_wdir()
        print(f"Music directory: {self.mdownload.get_music_path()}")
        print(f"Destination dir. {target_dir}")

        if target_dir == Path.cwd():
            print("Working directory changed succesfuly!")
            # change back to original dir and remove dummy folder
            os.chdir(prog_dir)
            os.rmdir(target_dir)
        
        else:
            print("Working directory not changed")
            return 3

        print("\nSet-up test PASSED!")
        return 0 
    
    # currently this is unneeded thus we will not implement this at the time 
    def authentificate(self):
        pass

    def authorize(self):
        
        # create enviorment file 
        load_dotenv(".env")
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.oauth.create_env_file(client_id, client_secret)
        if os.path.exists(self.oauth.env_file):
            print(f"{self.oauth.env_file} file created!")
        else:
            print("Fail to create .env file...")
            return 1

        # test authorization proceess with {not curretnly :"and without popup"}
        for val in [True]:
            print(f"Testing authorization with popup={val}")
            self.oauth.user_authorization(popup=val)
            if self.oauth.access_token:
                print("Access token retrieved!")
            else:
                print("No access token retireved...")
                return 2
            
            if self.oauth.refresh_token:
                print("Refresh token retrieved!")
            else:
                print("No refresh toeken retrieved...")
                return 3
            
        # check if values have been store in environment
        load_dotenv("dummy.env")
        tokens = ["SPOTIFY_ACCESS_TOKEN", "SPOTIFY_REFRESH_TOKEN", "EXPIRATION_DATE"]
        for token in tokens:
            if os.getenv(token):
                print(f"{token} stored in .env!")
            else:
                print(f"{token} not stored in .env file...")
                return 4

        # get new access_token via refresh token
        self.oauth.access_token = None
        self.oauth.refresh_access_token()
        if self.oauth.access_token:
            print("Access token refreshed succesfully!")
        else:
            print("Refresh process failed..") 
            return 5

        # remove dummy .env
        os.remove(self.oauth.env_file)
        print("\nOAuthorization test PASSED!")
        return 0

    def get_local_songs(self):
        pass

    def get_spotify_playlist(self):
        pass

    def download_songs(self):
        pass

    def edit_metadata(self):
        pass

def main():
    #  set up parser for arguments 
    parser = argparse.ArgumentParser(
        prog="m_downloader",
        description="Music Downloader with setting parameters and tester",
        usage="%(prog)s [--help] [--test OPTION] [--target-folder PATH] [--playlist NAME]")
    
    # add arguments 
    parser.add_argument("--test",
                        choices=["setup", "authent", "authorize", "local_songs",
                                "get_playlist", "download_songs", "edit_metadata"],
                        help="Test program setting (used for development).")
    
    parser.add_argument("--target-folder",
                        help="Set-up destination folder. If folder dosen't exist create it.")
    
    parser.add_argument("--playlist",
                        help="Set-up Spotify playlist to get playlists from.")
    
    # extract arguments 
    args = parser.parse_args()
    
    # check if no arguments where given and show usage message
    if not any([args.test, args.target_folder, args.playlist]):
        print("""No arguments were given...
              Intended use:

              m_downloader --target_folder 'destination folder' --playlist 'spotify playlist' --test 'testing option'

              Note:
                - For initial set-up both --target_folder and --playlist are mandatory.
                  After initial set-up, both are used to change the initial setting, thus
                  only one is really needed.
              
                - For a description of the arguments and their usage do: `m_downloader --help`
              """)
        sys.exit()

    # set up tester only if on testing mode
    if args.test:
        test = Tester()

        # run test depending on argument
        if args.test == "setup":
            test.setup()
        elif args.test == "authent":
            test.authenticate()
        elif args.test == "authorize":
            test.authorize()
        elif args.test == "local_songs":
            test.get_local_songs()
        elif args.test == "get_playlist":
            test.get_spotify_playlist()
        elif args.test == "download_songs":
            test.download_songs()
        elif args.test == "edit_metadata":
            test.edit_metadata()

        # exit program after running test
        return
        

if __name__ == "__main__":
    main()