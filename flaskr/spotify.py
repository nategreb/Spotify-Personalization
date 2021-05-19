from flask import (
    Flask, render_template, request, Blueprint, redirect, url_for
)

from .spotify_reddit.recommendations import get_recommended_tracks


bp = Blueprint('recommend', __name__, url_prefix='')

@bp.route('recommend', methods=('POST', 'GET'))
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
            ids = get_recommended_tracks([artist],[genre],[song])
            return render_template('test.html', list=ids)
    return render_template('recommend.html')    