import argparse
import json
from spotipyExt.auth import SpotifyAuth, YoutubeAuth
import os
import sys
import youtube_dl

def makeStringName(track):
    return track['name'] + ' - ' + ' - '.join([artist['name'] for artist in track['artists']])

parser = argparse.ArgumentParser()
parser.add_argument('--playlist', '-p', action='store',
                    default=None,help='Playlist from user library to pull tracks from. \nPS: Format for Windows is "[playlist name]" \nPSS: Collaborative playlists will error')
parser.add_argument('--trackNumber','-n', action='store',type=int,
                    default=float('inf'), help='Number of tracks to pull.')
#adding an argument to control if you want to search for the extended mix
parser.add_argument('--extendedMix', '-em', action='store_true',
                    help='Adding -em will search for the extended mix of your songs. If it does not exist, it will search the orignal title.')
args = parser.parse_args()

#Spotipy Auth
sp_scope = 'user-library-read playlist-read-private' 
sp = SpotifyAuth.get_authenticated_service(scope=sp_scope)

# Google Auth
yt = YoutubeAuth.get_authenticated_service()

# need var to know if you are searching for the extend mix
extendedMix = False
if args.extendedMix:
    print('Setting ExtendedMix Var')
    searchExtendedMix = True

# method definition to download youtube audio
def youtube_download(trackName, trackURL, outputDirectory):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([trackURL])
            if os.path.isfile(outputDirectory + '_.mp3'):
                os.rename(outputDirectory + '_.mp3', outputDirectory + trackName + '.mp3')
        except:
            print("Video unable to be downloaded for " + trackName)

if args.playlist:
    print("args.playlist = " + args.playlist)
    tracks = sp.getTracksFromPlaylistName(args.playlist,limit=args.trackNumber)
else:
    tracks = sp.current_user_saved_tracks(limit=args.trackNumber)

trackURLs = []
outputDir = 'C:\\Users\\cuter\\Music\\Downloads\\Honey - Volli Molli\\'
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': outputDir+'%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

trackables = enumerate(tracks['items'])
    
for count, track  in trackables:
    trackname = makeStringName(track['track'])
    tracknameExtendedMix = trackname + ' extended mix'
    # create query for extended mix search
    query_result_extended_mix = yt.search().list(
            part = 'snippet',
            q = tracknameExtendedMix, # extended mix added to grab more of the song
            order = 'relevance', # You can consider using viewCount
            maxResults = 1,
            type = 'video', # Channels might appear in search results
            relevanceLanguage = 'en',
            safeSearch = 'moderate',
            ).execute()
    print("Searchs "+str(count))
    # create the extended mix URL
    trackURLExtendedMix = "http://www.youtube.com/watch?v=" + query_result_extended_mix['items'][0]['id']['videoId']
    #skip is to know if it needs to search for the original track without "Extended Mix"
    skip = True
    if searchExtendedMix:
        print('Looking for Extended Mix')
        try:
            youtube_download(tracknameExtendedMix, trackURLExtended, outputDir)
        except:
            #because of an error, we need to try without "extended mix" in the searchs
            print("Could NOT find extended mix")
            skip = False
        finally:
            # do the search without "extended mix"
            print("Looking for any song")
            if not skip:
                #need to put this here because it was havling my download limit
                query_result = yt.search().list(
                    part='snippet',
                    q=trackname,
                    order='relevance',  # You can consider using viewCount
                    maxResults=1,
                    type='video',  # Channels might appear in search results
                    relevanceLanguage='en',
                    safeSearch='moderate',
                ).execute()
                trackURL = "http://www.youtube.com/watch?v=" + query_result['items'][0]['id']['videoId']
                youtube_download(trackname, trackURL, outputDir)
    else:
        #need to put this here because it was havling my download limit to run 2 queries
        query_result = yt.search().list(
            part='snippet',
            q=trackname,
            order='relevance',  # You can consider using viewCount
            maxResults=1,
            type='video',  # Channels might appear in search results
            relevanceLanguage='en',
            safeSearch='moderate',
        ).execute()
        trackURL = "http://www.youtube.com/watch?v=" + query_result['items'][0]['id']['videoId']
        youtube_download(trackname, trackURL, outputDir)
