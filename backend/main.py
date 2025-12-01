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

def can_place_on_any_ruins(shapes, player):
    all_shapes = []
    for shape in shapes:
        all_shapes.append(gameStart.flip_and_rotate(shape))
    for ruin_r, ruin_c in player.ruins_locations:
        for oriented in all_shapes:
            for i in range(len(oriented)):
                for j in range(len(oriented[0])):
                    if oriented[i][j] == 1:
                        anchor_r = ruin_r - i
                        anchor_c = ruin_c - j
                        if check_valid(player.current_grid, oriented, anchor_r, anchor_c):
                            return True
    return False

def check_valid(board, shape, start_r, start_c):
    rows, cols = len(board), len(board[0])
    for i in range(len(shape)):
        for j in range(len(shape[0])):
            if shape[i][j] == 1:
                r, c = start_r + i, start_c + j
                if r < 0 or r >= rows or c < 0 or c >= cols:
                    return False
                if board[r][c] not in ("0", "Ruins"):
                    return False
    return True

@app.post("/api/draw-card")
async def draw_card(Authorization: Optional[str] = Header(None)):
    global game_session
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = Authorization.split(" ")[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        player_id = decoded["player_id"]
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    player = game_session.players.get(player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
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

        # Check if season is over or deck is exhausted
        if game_session.season_time <= 0 or game_session.deck_index >= len(game_session.deck):
            if game_session.season_index >=3:
                # end game
                return {"error": "Game Over"}

        # Draw card
        card = game_session.deck[game_session.deck_index]
        game_session.deck_index += 1
        player.ruins_fallback = False

        # Handle ruins logic
        if card.type == "Ruins":
            game_session.ruins_required = True

        game_session.season_time -= card.cost
        game_session.current_card = card

        if game_session.ruins_required:
            if card.type == "Standard":
                card.ruinFlag = True
                game_session.ruins_required = False
                player.ruins_fallback = not (any(can_place_on_any_ruins(card.shape, player)))

                if player.ruins_fallback or (len(player.ruins_locations) == 0):
                    card = gameStart.terrainCard(card.name, card.cost, [[["Forest"]], [["Village"]], [["Farm"]], [["Water"]], [["Monster"]]], "Standard")


        print(f"Drew card: {card.name}, Cost: {card.cost}, Remaining Season Time: {game_session.season_time}")
        print(f"Deck: {[c.name for c in game_session.deck[game_session.season_index:]]}")

        return card.to_dict()

    except Exception as e:
        return {"error": str(e)}  
    
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

    # Determine which two scoring cards apply this season
    score_func_1 = game_session.score_types[game_session.season_index % 4]
    score_func_2 = game_session.score_types[(game_session.season_index + 1) % 4]
    print(score_func_1)
    print(score_func_2)

    score_letters = ["A", "B", "C", "D"]
    letter1 = score_letters[game_session.season_index % 4]
    letter2 = score_letters[(game_session.season_index + 1) % 4]

    breakdown = {
        letter1: 0,
        letter2: 0,
        "coins": 0,
        "monsters": 0,
        "total": 0
    }

    # Score each player (or just 1 if single-player)
    print(game_session.players)
    for player in game_session.players.values():
        grid = player.current_grid

        score1 = score_func_1(grid)
        score2 = score_func_2(grid)
        coins = player.coins
        monsters = -gameStart.monster_penalty(grid)

        season_total = score1 + score2 + coins + monsters
        player.score += season_total
        print(score1)
        print(score2)
        print(coins)
        print(monsters)
        print(player.score)

        breakdown[letter1] = score1
        breakdown[letter2] = score2
        breakdown["coins"] = coins
        breakdown["monsters"] = monsters
        breakdown["total"] = player.score

    # Advance the game to the next season
    season_result = start_new_season()
    if "error" in season_result:
        # This means game over
        return {
            "season": game_session.season_index,
            "breakdown": breakdown,
            "gameOver": True
        }

    # Normal season transition
    return {
        "season": game_session.season_index,
        "breakdown": breakdown,
        "gameOver": False
    }
    
@app.post("/api/coin-check")
async def coin_check(Authorization: Optional[str] = Header(None)):
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = Authorization.split(" ")[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        player_id = decoded["player_id"]
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    player = game_session.players.get(player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    return {"coins": player.coins}

class ValidationPayload(BaseModel):
    new_grid: List[List[str]]
    
@app.post("/api/validate")
async def validatePlacement(payload: ValidationPayload, Authorization: Optional[str] = Header(None)):
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = Authorization.split(" ")[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        player_id = decoded["player_id"]
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

    # Retrieve the Player object
    player = game_session.players.get(player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    card = game_session.current_card
    if player.ruins_fallback:
        card = gameStart.terrainCard(card.name, card.cost, [[["Forest"]], [["Village"]], [["Farm"]], [["Water"]], [["Monster"]]], "Standard")
    
    is_valid, message = gameStart.validate_placement(
        player.current_grid,
        payload.new_grid,
        card,
        player
    )

    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    # Commit the new grid + update history
    player.grid_history.append(player.current_grid)
    player.current_grid = payload.new_grid
    for mountain in player.mountain_locations[:]:
        y, x = mountain
        if gameStart.check_orthogonal_neighbors(player.current_grid, y, x):
            player.coins += 1
            player.mountain_locations.remove(mountain)

    return {"success": True, "message": "Move validated"}


import uuid
SECRET_KEY = "Life from the Loam 1G | Sorcery | Return up to three target land cards from your graveyard to your hand. Dredge 3"
@app.post("/api/create-player")
def create_player():
    player_id = str(uuid.uuid4())
    token = jwt.encode({"player_id": player_id}, SECRET_KEY, algorithm="HS256")
    game_session.players[player_id] = gameStart.Player(player_id, sample_grid)

    return {"playerToken": token}
