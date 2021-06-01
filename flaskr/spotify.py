from flask import (
    Flask, render_template, request, Blueprint, redirect, url_for, session
)
import os, requests, secrets, string
from datetime import datetime, timedelta

import pkce
import spotipy
import spotipy.util as util

from .spotify_reddit.recommendations import get_recommended_tracks


bp = Blueprint('spotify', __name__, url_prefix='/spotify')


@bp.route('/recommend', methods=('POST', 'GET'))
def recommend():
    if request.method == 'POST':
        artist = request.form['artist']
        genre = request.form['genre']
        song = request.form['song']
        error = None

        if not artist:
            error = 'artist is required'
        elif not genre:
            error = 'genre is required'    
        elif not song:
            error = 'song is required'    
        
        if error is None:            
            #session.clear()         
            #session['token'] = None                          
            session['songs'] = get_recommended_tracks([artist],[genre],[song])
            session['query'] = f'{song} by {artist}'
            if session['songs'] is not None:                
                return redirect(url_for('spotify.playlist_generator'))
    return render_template('Recommend.html')    


@bp.route('/playlist', methods=('POST', 'GET'))
def playlist_generator():
    error = False
    authorized = check_token()
    if request.method == 'POST':        
        if authorized:
            isPublic = True if request.form['playlistType'] == 'true' else False
            create_playlist(request.form['title'], isPublic)
        else:
            return redirect(url_for('spotify.authorize'))
    if 'state' in request.args and 'code' in request.args:
        get_token() 
        authorized = True       
    return render_template('RecommendPlaylist.html', query=session.get('query'),list=session.get('songs'), error=error, authorized=authorized)


#redirects to Spotify OAuth Page 
@bp.route('/authorize')
def authorize():
    #if 'token' not in session:
    code_verifier, code_challenge = pkce.generate_pkce_pair()
    session['code_verifier'] = code_verifier
    session['state'] = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(9))
    return redirect(
        f"https://accounts.spotify.com/authorize?" \
        f"client_id={os.environ['SPOTIPY_CLIENT_ID']}&" \
        f"response_type=code&" \
        f"redirect_uri={url_for('spotify.playlist_generator', _external = True)}&" \
        f"code_challenge_method=S256&" \
        f"code_challenge={code_challenge}&" \
        f"state={session['state']}&" \
        f"scope=playlist-modify-private playlist-modify-public user-read-private user-read-email"
    )


#if user doesn't authorize this app or log in, then page will handle the 404 status code with message to client
@bp.app_errorhandler(404)
def app_not_authorized(error):
    return render_template('RecommendPlaylist.html', query=session.get('query'),list=session.get('songs'), authorized=False)


#after client authorizes the app, gets the token
#also, calls get_user_id() since we now have the token
def get_token(): 
    #if request.args.get('state') == session['state'] and not request.args.get('error'): 
    if not check_token():
        r = requests.post(
            'https://accounts.spotify.com/api/token', 
            data = {
                'client_id':os.environ['SPOTIPY_CLIENT_ID'],
                'grant_type':'authorization_code',
                'code':request.args.get('code'),
                'redirect_uri':url_for('spotify.playlist_generator', _external = True),
                'code_verifier':session['code_verifier']
            }
        ) 
        session['token'] = r.json()['access_token']    
        session['token_expiration_time'] = (datetime.now() + timedelta(seconds = r.json()['expires_in'])).replace(tzinfo=None)
        session['refresh_token'] = r.json()['refresh_token']
        session['refresh_token_used'] = False
        #after setting the token, can get user_id for subsequent calls
        session['user_id'] = requests.get(
                        'https://api.spotify.com/v1/me',
                        headers = {
                            'Accept':'application/json',
                            'Content-Type':'application/json',
                            'Authorization':f"Bearer {session['token']}"
                        }
                    ).json()['id']
    

#checks if token is valid. If not, then checks validity of refresh token. Set session accordingly.
#returns Boolean if valid
def check_token():
    if 'token' in session:
        #post request if the curretn token is invalid and it's not the refresh token.
        if datetime.now() <= session['token_expiration_time'].replace(tzinfo=None):
            #return redirect(url)
            return True
        elif not session['refresh_token_used']:
            r = requests.post(
                'https://accounts.spotify.com/api/token', 
                data = {
                    'grant_type':'refresh_token',
                    'refresh_token':session['refresh_token'],
                    'client_id':os.environ['SPOTIPY_CLIENT_ID']
                }
            )
            session['token'] = r.json()['access_token']    
            session['refresh_token_used'] = True
            session['token_expiration_time'] = (datetime.now() + timedelta(seconds = r.json()['expires_in'])).replace(tzinfo=None)            
            #return redirect(url)
            return True
    else:
        return False


#create playlist given user token without using Spotipy 
#kwargs for description, image, etc.
#creates and adds songs to the playlist 
def create_playlist(name, public, **kwargs):
    description = ''
    if 'description' in kwargs:
        description = kwargs['description']
    #creates a playlist in the user's spotify account with POST.
    r = requests.post(
            f"https://api.spotify.com/v1/users/{session['user_id']}/playlists",
            json = {
                'name':name,
                'description':description,
                'public':public
            },
            headers = {
                'Accept':'application/json',
                'Content-Type':'application/json',
                'Authorization':f"Bearer {session['token']}"
            }
    )
    #raises error based on POST 
    r.status_code
    r.raise_for_status()
    #using the playlist's id from the response, add song ids from session.
    query_tracks = ''
    #songs is an array of arrays [[title, id]]
    for song_arr in session['songs']:
        query_tracks += f"spotify:track:{song_arr[1]},"
    
    requests.post(
        f"https://api.spotify.com/v1/playlists/{r.json()['id']}/tracks?uris={query_tracks}",
        headers = {
            'Accept':'application/json',
            'Content-Type':'application/json',
            'Authorization':f"Bearer {session['token']}"
        }
    )