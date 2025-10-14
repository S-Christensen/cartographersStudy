from fastapi import FastAPI
from pydantic import BaseModel
from backend.gameStart import GameSession, run_season


app = FastAPI()

# Global game session for demo (in production, use per-user/session)
game_session = GameSession("session_001")
current_season = 0
season_initialized = False

class CardResponse(BaseModel):
    cardName: str
    allowedTerrains: list

def get_allowed_terrains(card):
    # Example: extract unique terrain types from card.shapes
    terrains = set()
    for shape in card.shapes:
        for row in shape:
            for cell in row:
                if isinstance(cell, str):
                    terrains.add(cell)
    return list(terrains)

@app.post("/api/draw-card", response_model=CardResponse)
def draw_card():
    global current_season, season_initialized
    # If deck is empty or not initialized, run the next season
    if not season_initialized or not game_session.deck:
        run_season(game_session, game_session.deck, game_session.monster_deck, game_session.score_types, current_season)
        current_season += 1
        season_initialized = True
        if not game_session.deck:
            return {"cardName": "None", "allowedTerrains": []}
    card = game_session.deck.pop(0)
    allowed_terrains = get_allowed_terrains(card)
    game_session.current_card = card
    return {
        "cardName": card.name,
        "allowedTerrains": allowed_terrains
    }