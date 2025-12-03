from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
import jwt
from fastapi.middleware.cors import CORSMiddleware
import gameStart
import math
import random
import terrainCard
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cartographers-study.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openRooms = {}
season_initialized = False

sample_grid = [["0" for _ in range(11)] for _ in range(11)]
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

class RoomCodePayload(BaseModel):
    roomCode: str

def reset_game(code, size):
    if not code:
        raise HTTPException(status_code=400, detail="Room code required")

    openRooms[code] = gameStart.initialize_session()
    deck, monster_deck = gameStart.build_decks()
    score_types, score_types_names = gameStart.select_scoring_cards()

    deck.append(monster_deck[0])
    random.shuffle(deck)

    session = openRooms[code]
    session.deck = deck
    session.monster_deck = monster_deck
    session.score_types = score_types
    session.score_types_names = score_types_names
    session.season_index = 0
    session.season_time = 8
    session.season_initialized = True
    session.current_card = deck[0]
    session.max_players = size

    return {"status": "reset", "message": f"Game session {code} initialized"}


@app.post("/api/session")
def get_session(payload: RoomCodePayload):
    code = payload.roomCode.strip()
    return {
        "scoreTypes": openRooms[code].score_types,
        "scoreTypesNames": openRooms[code].score_types_names,
        "seasonTime": openRooms[code].season_time,
        "currentSeason": openRooms[code].season_index,
        "currentCard": openRooms[code].current_card.to_dict() if hasattr(openRooms[code], "current_card") else None
    }

def can_place_on_any_ruins(shapes, player):
    all_orientations = []
    for shape in shapes:
        for oriented in gameStart.flip_and_rotate(shape):
            all_orientations.append(oriented)
    print(all_orientations)

    for ruin_r, ruin_c in player.ruins_locations:
        print("Ruin Coords:")
        print(ruin_r)
        print(ruin_c)
        print(player.current_grid)

        # Skip if ruin already filled
        if player.current_grid[ruin_r][ruin_c] != "Ruins":
            continue

        for oriented in all_orientations:
            rows, cols = oriented.shape
            for i in range(rows):
                for j in range(cols):
                    if str(oriented[i][j]) != 0:
                        anchor_r = ruin_r - i
                        anchor_c = ruin_c - j
                        if check_valid(player.current_grid, oriented, anchor_r, anchor_c):
                            return True
    return False


def check_valid(board, shape, start_r, start_c):
    rows, cols = len(board), len(board[0])
    for i in range(shape.shape[0]):
        for j in range(shape.shape[1]):
            if str(shape[i][j]) != 0:
                r, c = start_r + i, start_c + j
                if r < 0 or r >= rows or c < 0 or c >= cols:
                    return False
                if board[r][c] not in ("0", "Ruins"):
                    return False
    return True

@app.post("/api/draw-card")
async def draw_card(payload: RoomCodePayload, Authorization: Optional[str] = Header(None)):
    code = payload.roomCode.strip()
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = Authorization.split(" ")[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        player_id = decoded["player_id"]
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    player = openRooms[code].players.get(player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    try:
        # Initialize game session if needed
        if not hasattr(openRooms[code], "season_initialized") or not openRooms[code].season_initialized:
            openRooms[code] = gameStart.initialize_session()
            deck, monster_deck = gameStart.build_decks()
            score_types = gameStart.select_scoring_cards()

            deck.append(monster_deck[0])
            random.shuffle(deck)

            openRooms[code].deck = deck
            openRooms[code].monster_deck = monster_deck
            openRooms[code].score_types = score_types
            openRooms[code].season_index = 0
            openRooms[code].deck_index = 0
            openRooms[code].season_time = 8 - math.ceil((openRooms[code].season_index + 1) / 2.0)
            openRooms[code].season_initialized = True
            openRooms[code].current_card = deck[0]

        # Check if season is over or deck is exhausted
        if openRooms[code].season_time <= 0 or openRooms[code].deck_index >= len(openRooms[code].deck):
            if openRooms[code].season_index >=3:
                # end game
                return {"error": "Game Over"}

        # Draw card
        deckIndex = openRooms[code].deck_index
        card = openRooms[code].deck[openRooms[code].deck_index]
        player.ruins_fallback = False

        # Handle ruins logic
        if card.type == "Ruins":
            if deckIndex == openRooms[code].deck_index:
                openRooms[code].deck_index += 1
            openRooms[code].ruins_required = True

        openRooms[code].current_card = card

        if openRooms[code].ruins_required:
            if card.type == "Standard":
                card.ruinFlag = True
                openRooms[code].ruins_required = False
                player.ruins_fallback = not can_place_on_any_ruins(card.shape, player)

                if player.ruins_fallback or (len(player.ruins_locations) == 0):
                    card = gameStart.terrainCard(card.name, card.cost, [[["Forest"]], [["Village"]], [["Farm"]], [["Water"]], [["Monster"]]], "Standard")
        if card.type == "Monster":
            card = monsterize(card, openRooms[code], player)

        print(f"Drew card: {card.name}, Cost: {card.cost}, Remaining Season Time: {openRooms[code].season_time-card.cost}")
        print(f"Deck: {[c.name for c in openRooms[code].deck[openRooms[code].season_index:]]}")

        return card.to_dict()

    except Exception as e:
        return {"error": str(e)}  
    
def start_new_season(code):
    if openRooms[code].deck_index == 0:
        return {"status": "new season started", "season": openRooms[code].season_index}

    openRooms[code].season_index += 1
    if openRooms[code].season_index >= 4:
        return {"error": "Game Over"}
    openRooms[code].deck, dummy = gameStart.build_decks()
    openRooms[code].deck.append(openRooms[code].monster_deck[openRooms[code].season_index])
    random.shuffle(openRooms[code].deck)

    openRooms[code].deck_index = 0
    season_times = [8, 8, 7, 6]
    openRooms[code].season_time = season_times[openRooms[code].season_index]

    return {"status": "new season started", "season": openRooms[code].season_index}

@app.post("/api/end-season")
async def end_season(payload: RoomCodePayload):
    code = payload.roomCode.strip()


    # Determine which two scoring cards apply this season
    score_func_1 = openRooms[code].score_types[openRooms[code].season_index % 4]
    score_func_2 = openRooms[code].score_types[(openRooms[code].season_index + 1) % 4]
    print(score_func_1)
    print(score_func_2)

    score_letters = ["A", "B", "C", "D"]
    letter1 = score_letters[openRooms[code].season_index % 4]
    letter2 = score_letters[(openRooms[code].season_index + 1) % 4]

    breakdown = {
        letter1: 0,
        letter2: 0,
        "coins": 0,
        "monsters": 0,
        "total": 0
    }

    # Score each player (or just 1 if single-player)
    print(openRooms[code].players)
    for player in openRooms[code].players.values():
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
    season_result = start_new_season(code)
    if "error" in season_result:
        # This means game over
        session = openRooms.pop(code)
        podium = []
        for guy in session.players.values():
            podium.append(guy.score)
        podium = sorted(podium)

        return {
            "season": openRooms[code].season_index,
            "breakdown": breakdown,
            "gameOver": True,
            "podium": podium
        }

    # Normal season transition
    return {
        "season": openRooms[code].season_index,
        "breakdown": breakdown,
        "gameOver": False
    }
    
@app.post("/api/coin-check")
async def coin_check(payload: RoomCodePayload, Authorization: Optional[str] = Header(None)):
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = Authorization.split(" ")[1]
    try:
        code = payload.roomCode.strip()
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        player_id = decoded["player_id"]
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    player = openRooms[code].players.get(player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    return {"coins": player.coins}

class ValidationPayload(RoomCodePayload):
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
    
    code = payload.roomCode.strip()

    # decode token, find player, etc.
    session = openRooms.get(code)
    if not session:
        raise HTTPException(status_code=404, detail="Room not found")

    player = session.players.get(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")


    # Retrieve the Player object
    card = session.current_card
    seasontime = session.season_time
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
    if session.submissions == session.max_players:
        session.submissions = 0
    session.submissions += 1
    timeElapsed = 0
    while session.submissions != session.max_players:
        player.locked= True
        await asyncio.sleep(1)
        timeElapsed += 1
        if timeElapsed >= 1500:
            openRooms.pop(code)
            return {"success": False, "message": "Room Closed due to inactivity"}
    
    player.locked= False
    if openRooms[code].season_time == seasontime:
        openRooms[code].deck_index += 1
        openRooms[code].season_time -= card.cost

    return {"success": True, "message": "Move validated"}


import uuid
SECRET_KEY = "Life from the Loam 1G | Sorcery | Return up to three target land cards from your graveyard to your hand. Dredge 3"
class RoomSetupPayload(BaseModel):
    roomCode: str
    roomSize: Optional[int] = None

@app.post("/api/create-player")
async def create_player(payload: RoomSetupPayload):
    code = payload.roomCode.strip()
    size = payload.roomSize
    if not code:
        raise HTTPException(status_code=400, detail="Room code required")

    player_id = str(uuid.uuid4())
    token = jwt.encode({"player_id": player_id, "room_code": code}, SECRET_KEY, algorithm="HS256")

    if code not in openRooms:
        openRooms[code] = gameStart.GameSession(code)
        reset_game(code, size)
    if len(openRooms[code].players) >= openRooms[code].max_players:
        raise HTTPException(status_code=403, detail="Room is full")

    openRooms[code].players[player_id] = gameStart.Player(player_id, sample_grid)
    timeElapsed = 0
    while len(openRooms[code].players) != openRooms[code].max_players:
        openRooms[code].players[player_id].locked= True
        await asyncio.sleep(1)
        timeElapsed += 1
        if timeElapsed >= 1500:
            openRooms.pop(code)
            raise HTTPException(status_code=405, detail="Room Timeout. Try Again")
    openRooms[code].players[player_id].locked= False
        
    openRooms[code].seating_order.append(player_id)
    print(openRooms[code].players)

    return {"playerToken": token}

def can_place_shape(shapes, player):
    all_orientations = []
    for shape in shapes:
        for oriented in gameStart.flip_and_rotate(shape):
            all_orientations.append(oriented)

    for ruin_r in range(len(player.current_grid)):
        for ruin_c in range(len(player.current_grid[0])):

            # Skip if ruin already filled
            if player.current_grid[ruin_r][ruin_c] != "Ruins" and player.current_grid[ruin_r][ruin_c] != "0":
                continue

            for oriented in all_orientations:
                rows, cols = oriented.shape
                for i in range(rows):
                    for j in range(cols):
                        if str(oriented[i][j]) != 0:
                            anchor_r = ruin_r - i
                            anchor_c = ruin_c - j
                            if check_valid(player.current_grid, oriented, anchor_r, anchor_c):
                                return True
    return False

def monsterize(card, session, player):
    direction = None
    if card.name in {"Goblin Attack", "Gnoll Raid"}:
        direction = "left"
    else:
        direction = "right"
    neighbor = None
    n = len(session.seating_order)
    i = session.seating_order.index(player.id)
    if direction == "right":
        neighbor = session.seating_order[(i+1) % n]
    elif direction == "left":
        neighbor = session.seating_order[(i-1) % n]
    neighbor = session.players[neighbor]
  
    if can_place_shape(card.shape, neighbor):
        return card
    else:
        card = gameStart.terrainCard(card.name, card.cost, [[["Monster"]]], "Monster")
        player.ruins_fallback = True
        return card
    
@app.post("/api/mash")
async def mash(payload: RoomCodePayload, Authorization: Optional[str] = Header(None)):
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = Authorization.split(" ")[1]
    try:
        code = payload.roomCode.strip()
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        player_id = decoded["player_id"]
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    player = openRooms[code].players.get(player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    
    session = openRooms[code]
    
    direction = None

    if session.current_card.name in {"Goblin Attack", "Gnoll Raid"}:
        direction = "left"
    else:
        direction = "right"
    neighbor = None
    n = len(session.seating_order)
    i = session.seating_order.index(player.id)
    if direction == "right":
        neighbor = session.seating_order[(i+1) % n]
    elif direction == "left":
        neighbor = session.seating_order[(i-1) % n]
    neighbor = session.players[neighbor]

    return {
            "neighborGrid": neighbor.current_grid
            }

'''
class ValidationPayload(RoomCodePayload):
    new_grid: List[List[str]]
'''

@app.post("/api/unmash")
async def unmash(payload: ValidationPayload, Authorization: Optional[str] = Header(None)):
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = Authorization.split(" ")[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        player_id = decoded["player_id"]
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    code = payload.roomCode.strip()

    # decode token, find player, etc.
    session = openRooms.get(code)
    if not session:
        raise HTTPException(status_code=404, detail="Room not found")

    player = session.players.get(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")


    # Retrieve the Player object
    card = session.current_card
    seasontime = session.season_time
    if player.ruins_fallback:
        card = gameStart.terrainCard(card.name, card.cost, [[["Monster"]]], "Monster")
    
    session = openRooms[code]
    
    direction = None

    if session.current_card.name in {"Goblin Attack", "Gnoll Raid"}:
        direction = "left"
    else:
        direction = "right"
    neighbor = None
    n = len(session.seating_order)
    i = session.seating_order.index(player.id)
    if direction == "right":
        neighbor = session.seating_order[(i+1) % n]
    elif direction == "left":
        neighbor = session.seating_order[(i-1) % n]
    neighbor = session.players[neighbor]

    is_valid, message = gameStart.validate_placement(
        neighbor.current_grid,
        payload.new_grid,
        card,
        neighbor
    )

    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    # Commit the new grid + update history
    neighbor.grid_history.append(neighbor.current_grid)
    neighbor.current_grid = payload.new_grid
    for mountain in neighbor.mountain_locations[:]:
        y, x = mountain
        if gameStart.check_orthogonal_neighbors(neighbor.current_grid, y, x):
            neighbor.coins += 1
            neighbor.mountain_locations.remove(mountain)
    if session.submissions == session.max_players:
            session.submissions = 0
    session.submissions += 1
    timeElapsed = 0
    while session.submissions != len(session.players):
        player.locked=True
        await asyncio.sleep(1)
        timeElapsed += 1
        if timeElapsed >= 1500:
            openRooms.pop(code)
            return {"success": False, "message": "Room Closed due to inactivity"}
    player.ruins_fallback = False
    player.locked= False
    if openRooms[code].season_time == seasontime:
        openRooms[code].deck_index += 1
        openRooms[code].season_time -= card.cost

    return {"success": True, "message": "Move validated", "grid": player.current_grid}

@app.post("/api/busywait")
async def busywait(payload: RoomCodePayload, Authorization: Optional[str] = Header(None)):
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = Authorization.split(" ")[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        player_id = decoded["player_id"]
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    code = payload.roomCode.strip()

    session = openRooms.get(code)
    if not session:
        raise HTTPException(status_code=404, detail="Room not found")

    player = session.players.get(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return {"locked" :player.locked}
