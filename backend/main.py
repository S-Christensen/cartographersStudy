from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
import jwt
from fastapi.middleware.cors import CORSMiddleware
import gameStart
import math
import random
import terrainCard

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cartographers-study.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

game_session = gameStart.GameSession("session_001")
season_initialized = False
player_grids = {}
player_scores = {}
sample_grid = [[0 for _ in range(11)] for _ in range(11)]
sample_grid[1][3] = "Mountain"
sample_grid[2][8] = "Mountain"
sample_grid[5][5] = "Mountain"
sample_grid[8][2] = "Mountain"
sample_grid[9][7] = "Mountain"
sample_grid[1][5] = "Ruins"
sample_grid[2][1] = "Ruins"
sample_grid[2][9] = "Ruins"
sample_grid[8][1] = "Ruins"
sample_grid[8][9] = "Ruins"
sample_grid[9][5] = "Ruins"

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
    score_types, score_types_names = gameStart.select_scoring_cards()

    deck.append(monster_deck[0])
    random.shuffle(deck)

    game_session.deck = deck
    game_session.monster_deck = monster_deck
    game_session.score_types = score_types
    game_session.score_types_names = score_types_names
    game_session.season_index = 0
    game_session.season_time = 8
    game_session.season_initialized = True
    game_session.current_card = deck[0]
    #Change to player in future update
    game_session.mountain_locations = [(1, 3), (2, 8), (5, 5), (8, 2), (9, 7)]
    return {"status": "reset", "message": "Game session initialized"}

@app.get("/api/session")
def get_session():
    return {
        "scoreTypes": game_session.score_types,
        "scoreTypesNames": game_session.score_types_names,
        "seasonTime": game_session.season_time,
        "currentSeason": game_session.season_index,
        "currentCard": game_session.current_card.to_dict() if hasattr(game_session, "current_card") else None
    }

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
            game_session.season_index = 0
            game_session.deck_index = 0
            game_session.season_time = 8 - math.ceil((game_session.season_index + 1) / 2.0)
            game_session.season_initialized = True
            game_session.current_card = deck[0]
            game_session.mountain_locations = [(1, 3), (2, 8), (5, 5), (8, 2), (9, 7)]

        # Check if season is over or deck is exhausted
        if game_session.season_time <= 0 or game_session.deck_index >= len(game_session.deck):
            if game_session.season_index >=3:
                # end game
                return {"error": "Game Over"}

        # Draw card
        card = game_session.deck[game_session.deck_index]
        game_session.deck_index += 1

        # Handle ruins logic
        if card.name in ["TempleRuins", "OutpostRuins"]:
            game_session.ruins_required = True
            if game_session.deck_index < len(game_session.deck):
                card = game_session.deck[game_session.deck_index]
                game_session.deck_index += 1
            else:
                return {"error": "Deck exhausted after ruins"}

        game_session.season_time -= card.cost
        game_session.current_card = card

        print(f"Drew card: {card.name}, Cost: {card.cost}, Remaining Season Time: {game_session.season_time}")
        print(f"Deck: {[c.name for c in game_session.deck[game_session.season_index:]]}")

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
    
def start_new_season():
    global game_session

    game_session.season_index += 1
    if game_session.season_index >= 4:
        return {"error": "Game Over"}
    game_session.deck, dummy = gameStart.build_decks()
    game_session.deck.append(game_session.monster_deck[game_session.season_index])
    random.shuffle(game_session.deck)

    game_session.deck_index = 0
    season_times = [8, 8, 7, 6]
    game_session.season_time = season_times[game_session.season_index]

    return {"status": "new season started", "season": game_session.season_index}

@app.post("/api/end-season")
async def end_season():
    global game_session

    try:
        result = start_new_season()
        if "error" in result:
            return result
        return result
    except Exception as e:
        return {"error": str(e)}
    
class Card(BaseModel):
    id: str
    cost: int
    shape: List[List[str]]
    terrainOptions: List[str]
    type: str
    ruinFlag: bool
    
class ValidationPayload(BaseModel):
    new_grid: List[List[str]]
    card: Card
    
@app.post("/api/validate")
async def validatePlacement(payload: ValidationPayload, Authorization: Optional[str] = Header(None)):
    # Verify token
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = Authorization.split(" ")[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        player_id = decoded["player_id"]
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

    stored_grid = player_grids[player_id]

    is_valid, message = gameStart.validate_placement(
        stored_grid,
        payload.new_grid,
        payload.card,
    )

    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    # Save new grid and return success
    player_grids[player_id] = payload.new_grid
    return {"success": True, "message": "Move validated"}

import uuid
SECRET_KEY = "Life from the Loam 1G | Sorcery | Return up to three target land cards from your graveyard to your hand. Dredge 3"
@app.post("/api/create-player")
def create_player():
    player_id = str(uuid.uuid4())
    token = jwt.encode({"player_id": player_id}, SECRET_KEY, algorithm="HS256")
    player_grids[player_id] = sample_grid
    player_scores[player_id] = 0

    return {"playerToken": token}