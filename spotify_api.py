import urllib.parse
import requests
from datetime import datetime, timedelta
from flask import Flask, redirect, request, jasonify, session # use to create rest API's easily

app = Flask(__name__)
# access to flas session (store data somewhere and retrieve it later)
app.secret_key="44rjtg8f9-887l-5720-abc4-7k777012731" # random key

# app constants 
CLIENT_ID = ""
CLIENT_SECRET = ""
REDIRECT_URL = "http://localhost:8080/callback"

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"

@app.route("/")
def index():
    return "Welcome to AutoMP3 <a href='/login'>Login with Spotify</a>"

# endpoint to redirect to spotify login page
@app.route("/login")
def login():
    # permissions scopes requeired (the two bellow)
    scope = "user-read-private user-read-email"

    parameters = {
        "client_id" : CLIENT_ID,
        "response_type" : "code",
        "scope" : scope,
        "redirect_url" : REDIRECT_URL,
        "show_dialog" : True              #debugging purpose (check login)
    }
    # authentification url; can be done using request but spotify offers a url
    # that acts as a request.get 
    auth_url  = f"{AUTH_URL}?{urllib.parse.urlencode(parameters)}"

    return redirect(auth_url)

# callback endpoint: retrun link after loging into spotify
@app.route("/callbalck")
def callback():
    # if log in is not succesful 
    if "error" in request.args:
        return jasonify({"error": request.args["error"]})
    
    # if code aka succesful login -> request body building to get access_token
    if "code" in request.args:
        req_body = {
            "code": request.args["code"],
            "grant_time": "authorization_code",
            "redirect_url": REDIRECT_URL,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
        # send request
        response = request.post(TOKEN_URL, data=req_body)
        # get token information
        token_info = response.json()

        session["access_token"] = token_info["access_token"]
        session["refresh_token"] = token_info["refresh_token"]
        # create time stamp when token expiress 
        session["expires_at"] = datetime.now().timestamp() + token_info["expires_in"]

        return redirect("/playlist")
    
    @app.route("/playlist")
    def get_playlist():
        # check it access token was stored in session, if not go to login
        if "access_token" not in session:
            return redirect("/login")
        
        # get new acess token via refresh token
        if datetime.now().timestamp() > session["expires_at"]:
            return redirect("/refresh-token")
        
        # retrieve users laylist 
        headers = {
            "Authorization" - f"Bearer {session["access_token"]}",
        }
        # ask for playlist
        respose = request.get(API_BASE_URL + "me/playlist", headers=headers)
        playlists = response.json() # extract playlists 

        return jasonify(playlists)

app.route("/refresh-token")
def refresh_token():

    if "refresh_token" not in session:
        return redirect("/login")
    
    if datetime.now().timestamp() > session["expires_at"]:
        req_body = {
            "grant_type": "refresh_token",
            "refresh_token": session["refresh_token"],
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }

        # send info 
        response = request.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()
        # update session
        session["access_token"] = new_token_info["access_token"]
        session["expire_at"] = datetime.now().timestamp + new_token_info["expires_in"]

    return redirect("/playlist")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)