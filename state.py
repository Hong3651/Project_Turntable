import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

STATE_PATH = Path("state.json")

@dataclass
class PlayerState:
    deck: List[str]
    history: List[str]

def load_state() -> Optional[PlayerState]:
    if not STATE_PATH.exists():
        return None
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[WARN] Could not load state.json. Starting with a new deck. Reason: {exc}")
        return None

    if not isinstance(data, dict):
        print("[WARN] Invalid state.json format. Starting with a new deck.")
        return None

    deck = data.get("deck", [])
    history = data.get("history", [])
    if not isinstance(deck, list) or not isinstance(history, list):
        print("[WARN] Invalid state.json contents. Starting with a new deck.")
        return None
    if not all(isinstance(track, str) for track in deck + history):
        print("[WARN] Invalid track path in state.json. Starting with a new deck.")
        return None

    return PlayerState(deck=deck, history=history)

def save_state(state: PlayerState) -> None:
    tmp_path = STATE_PATH.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(asdict(state), ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp_path, STATE_PATH)

def reset_state() -> None:
    if STATE_PATH.exists():
        STATE_PATH.unlink()
