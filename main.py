import signal
import sys
from pathlib import Path

from library import scan_mp3
from recommender import build_shuffle_deck
from player_vlc import play_track_blocking
from state import PlayerState, load_state, save_state, reset_state

MUSIC_FILE = Path("music")

# 전역 변수 
deck = []
history = []

def read_music_dir() -> str:
    if not MUSIC_FILE.exists():
        raise FileNotFoundError(
            "Missing 'music' file. Create a file named 'music' and put your music folder path in the first line."
        )
    music_dir = MUSIC_FILE.read_text(encoding="utf-8").strip()
    if not music_dir:
        raise ValueError("'music' file is empty.")
    return music_dir

def handle_exit(sig, frame):
    """Ctrl+C 또는 SIGTERM 시 상태 저장 후 종료"""
    print("\n[INFO] Saving state and exiting...")
    save_state(PlayerState(deck=deck, history=history))
    sys.exit(0)

def main():
    global deck, history
    
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    
    music_dir = read_music_dir()
    tracks = scan_mp3(music_dir)

    st = load_state()

    if st and st.deck:
        deck = st.deck
        history = st.history
        print(f"[INFO] Resuming saved deck. Remaining tracks: {len(deck)}")
    else:
        deck = build_shuffle_deck(tracks)
        history = []
        print(f"[INFO] New shuffled deck created. Total tracks: {len(deck)}")

    while True:
        if not deck:
            deck = build_shuffle_deck(tracks)
            history = []
            print("[INFO] Deck finished. Reshuffling...")

        track = deck.pop(0)

        try:
            play_track_blocking(track)
        except Exception as e:
            print(f"[WARN] Skip failed track: {track}\n       Reason: {e}")

        history.append(track)
        save_state(PlayerState(deck=deck, history=history))

if __name__ == "__main__":
    main()