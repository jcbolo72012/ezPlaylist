import spotipy, random, json
import spotipy.util as util

def spot(x):
    #loading client credentials
    with open('config.json') as (file):
        info = json.load(file)
    CLIENT_ID=str(info['CLIENT_ID'])
    CLIENT_SECRET=str(info['CLIENT_SECRET'])
    NAME=str(info['USERNAME'])


    #generating token from client info and creating spotify client
    token = util.prompt_for_user_token(NAME, scope='playlist-modify-public', client_id=CLIENT_ID,
                                       client_secret=CLIENT_SECRET, redirect_uri='https://localhost:8080')
    sp = spotipy.Spotify(auth=token)
    u_data = sp.current_user()
    u_id = u_data["id"]

    #creating list of supported genres, then randomizing into new list
    genres = ['hip-hop', 'pop','country','classical','rock','dance','edm','electronic']                                  
    seedGenres = [random.choice(genres),random.choice(genres),random.choice(genres),random.choice(genres),random.choice(genres)]

    #creating new playlist
    title = "ezPlaylist - " + (str)(random.randrange(1, 10**3))
    p_data = sp.user_playlist_create(u_id, title)
    p_id = p_data["id"]

    #grabbing list of recommended songs from Spotify API, based on our valence val, genres, and targeted popularity
    recom = sp.recommendations(limit=50, target_valence=x, seed_genres=seedGenres,
                               min_popularity=60, max_popularity=100, target_popularity=90)

    #adding song data from recommendations to list
    tracks = recom['tracks']

    #parsing list for song URIs, then using to add songs to playlist
    uris = []
    for i in tracks:
        uris.append(i["uri"])
    sp.user_playlist_add_tracks(u_id,p_id,uris)

    #printing valence value, then returning playlist id
    print("Valence: " + str(x) + "\n")
    return(p_id)    

