import dj_lib
import VS

def run(land_playlist = 'land.m3u', outro = True):
    global plist
    dj_lib.disable()
    plist=VS.musicAddList('land.m3u')

def setup(mainroom, play_land_music = True):
    global plist
    if play_land_music:
        VS.musicPlayList(plist)


