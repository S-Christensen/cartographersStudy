import json
from api.gameStart import GameSession, run_season

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

    try:
        if not season_initialized or not game_session.deck:
            run_season(game_session, game_session.deck, game_session.monster_deck, game_session.score_types, current_season)
            current_season += 1
            season_initialized = True

        if not game_session.deck:
            body = {
                "cardName": "None",
                "allowedTerrains": [],
                "shape": [[0]]
            }
        else:
            card = game_session.deck.pop(0)
            allowed_terrains = get_allowed_terrains(card)
            shape = card.shapes[0] if hasattr(card, 'shapes') and card.shapes else [[1]]
            game_session.current_card = card

            body = {
                "cardName": card.name,
                "allowedTerrains": allowed_terrains,
                "shape": shape
            }

        return (
            200,
            {"Content-Type": "application/json"},
            json.dumps(body)
        )

    except Exception as e:
        return (
            500,
            {"Content-Type": "application/json"},
            json.dumps({"error": str(e)})
        )