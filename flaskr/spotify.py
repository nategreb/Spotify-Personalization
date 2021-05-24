from flask import (
    Flask, render_template, request, Blueprint, redirect, url_for, session
)
import os
import requests
import secrets
import string

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
            session.clear()         
            session['token'] = None                          
            session['songs'] = get_recommended_tracks([artist],[genre],[song])
            session['query'] = f'{song} by {artist}'
            if session['songs'] is not None:                
                return redirect(url_for('spotify.playlist_generator'))
    return render_template('Recommend.html')    


@bp.route('/playlist', methods=('POST', 'GET'))
def playlist_generator():
    if session['token'] is None:
        if request.method == 'POST':
            return redirect(url_for('spotify.authorize'))
        if request.args.get('state') is not None and request.args.get('code') is not None:
            login()
    #check validity of token(has expiration in post request)
    #check query paramters if error. Show on page if the user didn't log in 
    return render_template('RecommendPlaylist.html', query=session.get('query'),list=session.get('songs'))


#redirects to Spotify OAuth Page 
@bp.route('/authorize')
def authorize():
    if session['token'] is None:
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
            f"state={session['state']}"
        )


#after client authorizes the app, gets the token
def login(): 
    if request.args.get('state') == session['state'] and not request.args.get('error'):
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