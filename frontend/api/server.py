# /api/draw-card.py

from typing import List, Any
from backend.gameStart import GameSession, run_season

# Global game session (for demo only)
game_session = GameSession("session_001")
current_season = 0
season_initialized = False

def get_allowed_terrains(card):
    terrains = set()
    for shape in card.shapes:
        for row in shape:
            for cell in row:
                if isinstance(cell, str):
                    terrains.add(cell)
    return list(terrains)

def handler(request):
    global current_season, season_initialized

    if not season_initialized or not game_session.deck:
        run_season(game_session, game_session.deck, game_session.monster_deck, game_session.score_types, current_season)
        current_season += 1
        season_initialized = True
        if not game_session.deck:
            return {
                "cardName": "None",
                "allowedTerrains": [],
                "shape": [[0]]
            }

    card = game_session.deck.pop(0)
    allowed_terrains = get_allowed_terrains(card)
    shape = card.shapes[0] if hasattr(card, 'shapes') and card.shapes else [[1]]
    game_session.current_card = card

    return {
        "cardName": card.name,
        "allowedTerrains": allowed_terrains,
        "shape": shape
    }