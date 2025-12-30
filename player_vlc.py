import time
from pathlib import Path
import vlc

def play_track_blocking(track_path: str) -> None:
    instance = vlc.Instance()
    player = instance.media_player_new()

    media = instance.media_new(track_path)
    player.set_media(media)

    print(f"Now playing: {Path(track_path).name}")
    player.play()

    # 재생 시작 대기(일부 환경에서 필요)
    time.sleep(0.3)

    while True:
        state = player.get_state()
        if state in (vlc.State.Ended, vlc.State.Error, vlc.State.Stopped):
            break
        time.sleep(0.2)

    if player.get_state() == vlc.State.Error:
        raise RuntimeError(f"VLC failed to play: {track_path}")
