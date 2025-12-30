import random
from typing import List

def build_shuffle_deck(tracks: List[str]) -> List[str]:
  
    # 복사본 생성
    deck = list(tracks)
    
    # 덱 섞기
    random.shuffle(deck)
    
    return deck