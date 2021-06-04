from .spotify_playlists import PrivatePlaylist, client


#a list of recommended track ids based on artists 
#Up to 5 seed values may be provided in any combination of seed_artists, seed_tracks and seed_genres.
#@param: artists, tracks: String[]
#returns [[String, String]]
def get_recommended_tracks(artists, tracks, **kwargs):
    if len(artists) == 0 or len(tracks) == 0:
        print("at least one of artists, genres, and tracks are required")
    else:
        artists = seed_artists(artists)
        tracks = seed_tracks(tracks)
        if len(artists) > 0 and len(tracks) > 0 and len(artists) + len(tracks) <= 5:
            limit = 20
            if len(kwargs) > 0 and 'limit' in kwargs:                
                limit = kwargs['limit']
            songs = []
            if limit > 0 and limit <= 100:
                for track in client.recommendations(seed_artists=artists, seed_tracks=tracks, limit=limit)['tracks']:
                    songs.append([f"{track['name']} by {track['artists'][0]['name']}", track['id']])
                return songs
            else: 
                print("Limit size must be between 0 and 100, inclusive")
        else: 
            print("No ids were found for artists and/or tracks")
    return None 


#artists:String[]
#returns a list of ids corresponding to the list of artists
def seed_artists(artists):
    ids = []
    artists = artists[:5]
    for i in range(len(artists)):
        id = get_id(artists[i], 'artist')
        if id is not None:
            ids.append(id)
    return ids


#tracks: String[]
#returns a list of ids corresponding to the track names
def seed_tracks(tracks):
    ids = []
    tracks = tracks[:5]
    for i in range(len(tracks)):        
        id = get_id(tracks[i], 'track')
        if id is not None:
            ids.append(id)
    return ids


#helper function for getting an id 
#(query: String, kind: String)
#kind is the seed type 
def get_id(query, kind):    
    result = client.search(q=f"{kind}:{query}", type=kind, limit=1)
    if len(result) > 0 and len(result[kind+'s']['items']) > 0:
        return result[kind+'s']['items'][0]['id']
    return None