import time
from pathlib import Path
import vlc

def play_track_blocking(track_path: str) -> None:
    instance = vlc.Instance("--no-xlib", "--quiet")
    player = instance.media_player_new()

    media = instance.media_new(track_path)
    player.set_media(media)

    print(f"Now playing: {Path(track_path).name}")
    result = player.play()
    if result == -1:
        raise RuntimeError(f"VLC failed to start playback: {track_path}")

    # libVLC가 재생 상태로 진입할 시간을 짧게 둔다.
    time.sleep(0.3)

    while True:
        state = player.get_state()
        if state in (vlc.State.Ended, vlc.State.Error, vlc.State.Stopped):
            break
        time.sleep(0.2)

    if player.get_state() == vlc.State.Error:
        raise RuntimeError(f"VLC failed to play: {track_path}")
