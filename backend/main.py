# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import gameStart
import math
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cartographers-study.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

game_session = gameStart.GameSession("session_001")
current_season = 0
season_initialized = False

def get_allowed_terrains(card):
    terrains = set()
    for shape in card.shape:
        for row in shape:
            for cell in row:
                if isinstance(cell, str):
                    terrains.add(cell)
    return list(terrains)

@app.post("/api/reset-game")
def reset_game():
    global game_session

    game_session = gameStart.initialize_session()
    deck, monster_deck = gameStart.build_decks()
    score_types = gameStart.select_scoring_cards()

    deck.append(monster_deck[0])
    random.shuffle(deck)

    game_session.deck = deck
    game_session.monster_deck = monster_deck
    game_session.score_types = score_types
    game_session.index = 0
    game_session.season_time = 8
    game_session.season_initialized = True
    #Change to player in future update
    game_session.mountain_locations = [(1, 3), (2, 8), (5, 5), (8, 2), (9, 7)]
    return {"status": "reset", "message": "Game session initialized"}

@app.post("/api/draw-card")
async def draw_card():
    global game_session

    try:
        # Initialize game session if needed
        if not hasattr(game_session, "season_initialized") or not game_session.season_initialized:
            game_session = gameStart.initialize_session()
            deck, monster_deck = gameStart.build_decks()
            score_types = gameStart.select_scoring_cards()

            deck.append(monster_deck[0])
            random.shuffle(deck)

            game_session.deck = deck
            game_session.monster_deck = monster_deck
            game_session.score_types = score_types
            game_session.index = 0
            game_session.season_time = 8
            game_session.season_initialized = True
            game_session.mountain_locations = [(1, 3), (2, 8), (5, 5), (8, 2), (9, 7)]

        # Check if season is over or deck is exhausted
        if game_session.season_time <= 0 or game_session.index >= len(game_session.deck):
            return {"error": "Season over or deck exhausted"}

        # Draw card
        card = game_session.deck[game_session.index]
        game_session.index += 1

        # Handle ruins logic
        if card.name in ["TempleRuins", "OutpostRuins"]:
            game_session.ruins_required = True
            if game_session.index < len(game_session.deck):
                card = game_session.deck[game_session.index]
                game_session.index += 1
            else:
                return {"error": "Deck exhausted after ruins"}

        game_session.season_time -= card.cost
        game_session.current_card = card

        print(f"Drew card: {card.name}, Cost: {card.cost}, Remaining Season Time: {game_session.season_time}")
        print(f"Deck: {[c.name for c in game_session.deck[game_session.index:]]}")

        return card.to_dict()

    except Exception as e:
        return {"error": str(e)}  
    '''
    global current_season, season_initialized

    try:
        if not season_initialized or not game_session.deck:
            run_season(
                game_session,
                game_session.deck,
                game_session.monster_deck,
                game_session.score_types,
                current_season
            )
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
        shape = card.shape[0] if hasattr(card, 'shape') and card.shape else [[1]]
        game_session.current_card = card

        return {
            "cardName": card.name,
            "allowedTerrains": allowed_terrains,
            "shape": shape
        }
        card = game_session.deck.pop(0)
        allowed_terrains = get_allowed_terrains(card)
        shape = card.shape[0] if hasattr(card, 'shape') and card.shape else [[1]]
        game_session.current_card = card

        return {
            "cardName": card.name,
            "allowedTerrains": allowed_terrains,
            "shape": shape
        }        '''
      