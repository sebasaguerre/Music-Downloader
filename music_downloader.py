import os
import json
from pathlib import Path



class MusicDownloader:
    
    def __init__(self, extra=""):
        self.dest_folder = self.get_os_music_path(extra=extra) + self.load_confi()
        
        # change to target directory 
        os.chdir(self.desrt_folder)

    def authenticate(self):
        """Authenticate with Spotify API"""
        pass

    def get_os_music_path(self, extra=""):
        """Detect OS and on that basic get dir for music"""
        home = Path.home()
        music_dir = home / "Music"

        # go one level deeper 
        if extra:
            music_dir = music_dir / extra
            return music_dir 
            
        return music_dir 

    def load_confi(self, dest_file=None):
        """Load configurations"""

        if os.path.exists("configurarions.json"):
            with open("confgurations.json", "r") as fhand:
                    self.state = json.load(fhand)
                    
                    # change target folder
                    if not dest_file:
                        self.state["local_file"] = dest_file
                        json.dump(self.state, fhand)
        # initialize configurations
        else:
            self.state = {"local_file": dest_file}
            # save configuration
            with open("configurarions.json", "w") as fhand:
                json.dump(self.state, fhand)


    def get_local_songs(self):
        """Extract local songs"""

        self.local_songs = []

        # iterate over local files 
        for file in Path(".").iterdir():
            if file.is_file():
                # extract song name and added it to local files
                self.local_songs.append(file.name.split(".")[0])
        


    def get_spotify_playlist(self):
        pass

def main():
    pass

if __name__ == "__main__":
    main()
    

    