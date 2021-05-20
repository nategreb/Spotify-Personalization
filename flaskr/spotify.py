from flask import (
    Flask, render_template, request, Blueprint, redirect, url_for
)

from .spotify_reddit.recommendations import get_recommended_tracks


bp = Blueprint('recommend', __name__, url_prefix='')

@bp.route('recommend', methods=('POST'))
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
            songs = get_recommended_tracks([artist],[genre],[song])
            return render_template('RecommendPlaylist.html', query=f'{song} by {artist}',list=songs)
    return render_template('Recommend.html')    