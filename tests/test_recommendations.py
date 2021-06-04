import os
import tempfile

import pytest

from ..flaskr.spotify_reddit.recommendations import *


def test_genres():
    assert seed_genres('', '') == []
    #following asserts greater or equal to 0 but less than or equal to 5
    genres = seed_genres(['Kanye West', 'Eminem', 'Logic', 'Drake', 'Eminem'], 'artist')
    assert len(genres) <= 5
    assert len(genres) >= 0
    assert len(seed_genres('', '')) == 0


def test_recommended_tracks():
    assert get_recommended_tracks([''], ['']) is None
    #assert missing arguments
    artists = ['Kanye West']
    songs =  ['Monster']
    assert get_recommended_tracks(artists, None) is None
    assert get_recommended_tracks(None, songs) is None
    assert get_recommended_tracks(None, None) is None
    #test limit default, fringe cases, and allowed ones.
    assert len(get_recommended_tracks(artists, songs)) == 20
    assert len(get_recommended_tracks(artists, songs, limit=40)) == 40
    assert get_recommended_tracks(artists, songs, limit=101) == None
    assert get_recommended_tracks(artists, songs, limit=-1) == None

    songs = ['Monster','Runaway','Gold Digger','So Appalled','Blood Diamonds','Otis']
    artists = ['Kanye West','Jay Z','Eminem','Tupac','Rick Ross','Beyonce']
    assert get_recommended_tracks(artists, songs) is not None
   
    
def test_seed_tracks():\
    #assert more than 5 ids isn't returned
    songs = ['Monster','Monster','Monster','Monster','Monster','Monster']
    assert len(seed_tracks(songs)) == 5 
    assert len(seed_tracks([])) == 0

def test_seed_artists():
    #assert more than 5 ids isn't returned
    artists = ['Kanye West','Kanye West','Kanye West','Kanye West','Kanye West','Kanye West']
    assert len(seed_artists(artists)) == 5
    assert len(seed_tracks([])) == 0

    
