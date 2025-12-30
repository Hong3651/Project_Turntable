import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

STATE_PATH = Path("state.json")

@dataclass
class PlayerState:
    deck: List[str]
    history: List[str]

def load_state() -> PlayerState | None:
    if not STATE_PATH.exists():
        return None
    data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return PlayerState(deck=data.get("deck", []), history=data.get("history", []))

def save_state(state: PlayerState) -> None:
    STATE_PATH.write_text(json.dumps(asdict(state), ensure_ascii=False, indent=2), encoding="utf-8")

def reset_state() -> None:
    if STATE_PATH.exists():
        STATE_PATH.unlink()
