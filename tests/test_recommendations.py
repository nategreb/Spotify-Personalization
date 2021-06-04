import os
import tempfile

import pytest

from ..flaskr.spotify_reddit.recommendations import *


def test_recommended_tracks():
    assert get_recommended_tracks([], []) is None
    #assert missing arguments
    artists = ['Kanye West']
    songs =  ['Monster']
    assert get_recommended_tracks(artists, []) is None
    assert get_recommended_tracks([], songs) is None
    assert get_recommended_tracks([], []) is None
    #test limit default, fringe cases, and allowed ones.
    assert len(get_recommended_tracks(artists, songs)) == 20
    assert len(get_recommended_tracks(artists, songs, limit=40)) == 40
    assert get_recommended_tracks(artists, songs, limit=101) == None
    assert get_recommended_tracks(artists, songs, limit=-1) == None

    #test with one input for each
    songs = ['Monster']
    artists = ['Kanye West']
    assert get_recommended_tracks(artists, songs) is not None

    #test with seed combination is greater than 5
    songs = ['Monster','Runaway','Gold Digger','So Appalled','Blood Diamonds','Otis']
    artists = ['Kanye West','Jay Z','Eminem','Tupac','Rick Ross','Beyonce']
    assert get_recommended_tracks(artists, songs) is None

    #test combination where seeds combination is 5
    songs = ['Monster','Runaway','Gold Digger']
    artists = ['Kanye West','Jay Z']
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