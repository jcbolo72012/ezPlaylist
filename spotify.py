import spotipy
import spotipy.util as util
import random

def spot(x):
    token = util.prompt_for_user_token('bostonhacks', scope='playlist-modify-public', client_id='acee09a2147c4ba08136b74ac33ffd61', client_secret='98ec1927e041445397e039e55d690840', redirect_uri='https://localhost:8080')
    sp = spotipy.Spotify(auth=token)

    genres = ['hip-hop', 'pop','country','classical','rock','dance','edm','electronic']
    u_data = sp.current_user()
    u_id = u_data["id"]
                                                
    seedGenres = [random.choice(genres),random.choice(genres),random.choice(genres),random.choice(genres),random.choice(genres)]
    
    title = "ezPlaylist - " + (str)(random.randrange(1, 10**3))
    p_data = sp.user_playlist_create(u_id, title)
    p_id = p_data["id"]

    
    recom = sp.recommendations(limit=50, target_valence=x, seed_genres=seedGenres, min_popularity=60, max_popularity=100, target_popularity=90)
    tracks = recom['tracks']

    uris = []
    for i in tracks:
        uris.append(i["uri"])
        
    sp.user_playlist_add_tracks(u_id,p_id,uris)
    return(p_id)    

