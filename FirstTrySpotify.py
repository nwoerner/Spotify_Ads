from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from time import sleep

# SpotifyCredentials is a file used to store Client_ID, Client_Secret, and username for security
from SpotifyCredentials import Spotify_Client_ID, Spotify_Client_Secret, Spotify_username

class Spotify_App(object):
    def __init__(self):
        # Spotify Client Info
        self.Client_ID = Spotify_Client_ID
        self.Client_Secret = Spotify_Client_Secret
        self.username = Spotify_username
        self.redirect_uri = "https://www.spotify.com"
        self.scope = 'user-read-playback-state'
        self.Spotify_Playing = True
        self.Sample_Interval = 2.0

    # Code checks if the spotify token is expiered and returns a new one if it is else returns None.
    def Expired_Token_Check(self, token_info, token):
        if token_info.is_token_expired(token) is True:
            print("Token has expired")
            token = token_info.refresh_access_token(token['refresh_token'])
            return  token

    # Main Function - Checks if an ad is playing at a specified sample interval
    # and turns the spotify volume down to 0 if an ad is playing. 
    # Once the ad stops it turns the volume back up to the orignal volume.
    def No_Ad_Volume(self):
        token_info, token, sp = self.User_Auth()

        while self.Spotify_Playing == True:
            check_token = self.Expired_Token_Check(token_info, token)
            if check_token:
                token = check_token
                sp = spotipy.Spotify(auth=token['access_token'])
            
            Playing = sp.current_user_playing_track()
            if Playing == None:
                self.Spotify_Playing = False
                break
            else:
                # if Playing["is_playing"] is True:
                #     print("Spotify: playing")
                # elif Playing["is_playing"] is False:
                #     print("Spotify: paused")

                # wait_time = 0.0

                if Playing['currently_playing_type'] == "ad":
                    self.Set_Volume(0)
                    # wait_time = self.Wait(30000.0, Playing["progress_ms"])
                else:
                    self.Set_Volume(1)
                    # wait_time = self.Wait(Playing["item"]["duration_ms"],
                    #                       Playing["progress_ms"])

                sleep(self.Sample_Interval*2)
        
        self.No_Music(token_info=token_info, token=token, sp=sp)
    
    # Code checks at specified multiple of the sample interval if music is playing.
    # If Playing returns data loop breaks and No_Ad_Volume is called.
    def No_Music(self, token_info, token, sp):
        while self.Spotify_Playing == False:
            check_token = self.Expired_Token_Check(token_info, token)
            if check_token:
                token = check_token
                sp = spotipy.Spotify(auth=token['access_token'])
            
            Playing = sp.current_user_playing_track()
            if Playing:
                self.Spotify_Playing = True
                break
            else:
                sleep(self.Sample_Interval * 10)
        
        self.No_Ad_Volume()

    # Code uses pycaw to adjust the Spotify console application volume.
    def Set_Volume(self, Volume_Level):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                try:
                    if session.Process.name() == "Spotify.exe":
                        # print("volume.GetMasterVolume(): %s" % volume.GetMasterVolume())
                        volume.SetMasterVolume(Volume_Level, None)
                except AttributeError:
                    pass
    
    # Code attempst to Authenticate Users.
    # If it can it will return [token_info, token, sp].
    def User_Auth(self):
        client_credentials_manager = SpotifyClientCredentials(client_id=self.Client_ID,
                                                              client_secret=self.Client_Secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        token_info = SpotifyOAuth(username=self.username,
                                  scope=self.scope,
                                  client_id=self.Client_ID,
                                  client_secret=self.Client_Secret,
                                  redirect_uri=self.redirect_uri)
        if token_info:
            token = token_info.get_cached_token()
            sp = spotipy.Spotify(auth=token['access_token'])
        else:
            print("Can't get token info for", self.username)
        return [token_info, token, sp]

    def Wait(self, duration, progress, delay=1.0):
        wait_time = (duration - progress)/1000 + delay
        return wait_time

if __name__ == "__main__":
    Spotify_App().No_Ad_Volume()
