from fastapi import FastAPI
from pydantic import BaseModel
from backend.gameStart import GameSession, build_decks  # adjust import as needed

app = FastAPI()

# Global game session for demo (in production, use per-user/session)
game_session = GameSession("session_001")

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
    # Draw the next card from the deck
    if not game_session.deck:
        return {"cardName": "None", "allowedTerrains": []}
    card = game_session.deck.pop(0)
    allowed_terrains = get_allowed_terrains(card)
    game_session.current_card = card
    return {
        "cardName": card.name,
        "allowedTerrains": allowed_terrains
    }