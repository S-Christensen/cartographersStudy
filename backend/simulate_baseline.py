import copy
import random
import statistics
import numpy as np
import gameStart
from gameStart import GameSession, Player, validate_placement, flip_and_rotate

TERRAIN_TYPES = ["Forest", "Village", "Farm", "Water"]
RIFTLANDS_TERRAIN_TYPES = ["Forest", "Village", "Farm", "Water", "Monster"]

def assign_monster_quadrant(card):
    name = card.name

    if name == "Bugbear Assault":
        card.corner = "NE"
        card.direction = "down"

    elif name == "Kobold Onslaught":
        card.corner = "SW"
        card.direction = "up"

    elif name == "Goblin Attack":
        card.corner = "SE"
        card.direction = "left"

    elif name == "Gnoll Raid":
        card.corner = "NW"
        card.direction = "right"
    else:
        print(f"Warning: Unrecognized monster card '{name}'.")
        # Fallback so apply_ambush_rules still works
        card.corner = getattr(card, "corner", "NW")
        card.direction = getattr(card, "direction", "right")

    return card

def apply_ambush_rules(grid, card):
    shape = np.array(card.shape[0], dtype=object)
    h, w = shape.shape
    N = len(grid)

    corner = getattr(card, "corner", "NW")
    direction = getattr(card, "direction", "right")

    if corner == "NW":
        start_r, start_c = 0, 0
    elif corner == "NE":
        start_r, start_c = 0, N - 1
    elif corner == "SE":
        start_r, start_c = N - 1, N - 1
    elif corner == "SW":
        start_r, start_c = N - 1, 0
    else:
        start_r, start_c = 0, 0  # fallback

    DIRS = {
        "right": (0, 1),
        "left": (0, -1),
        "down": (1, 0),
        "up": (-1, 0)
    }
    dr, dc = DIRS.get(direction, (0, 1))

    for layer in range(N):
        r = start_r + (layer if start_r == 0 else -layer if start_r == N - 1 else 0)
        c = start_c + (layer if start_c == 0 else -layer if start_c == N - 1 else 0)

        for step in range(N):
            rr = r + dr * step
            cc = c + dc * step

            if rr < 0 or cc < 0 or rr + h > N or cc + w > N:
                continue

            legal = True
            for i in range(h):
                for j in range(w):
                    if shape[i][j] not in (0, "0"):
                        if grid[rr + i][cc + j] not in ("0", "Ruins"):
                            legal = False
                            break
                if not legal:
                    break

            if legal:
                new_grid = [row[:] for row in grid]
                for i in range(h):
                    for j in range(w):
                        if shape[i][j] not in (0, "0"):
                            new_grid[rr + i][cc + j] = "Monster"
                return new_grid

    return None


def best_riftlands_tile_placement(grid):
    rows, cols = len(grid), len(grid[0])

    for terrain in RIFTLANDS_TERRAIN_TYPES:
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] in ("0", "Ruins"):
                    new_grid = [row[:] for row in grid]
                    new_grid[r][c] = terrain
                    return new_grid

    return None

def random_sampled_placement(grid, card, player, max_attempts=200):
    rows, cols = len(grid), len(grid[0])

    orientations = []
    seen = set()
    for shape in card.shape:
        for variant in flip_and_rotate(np.array(shape, dtype=object)):
            key = tuple(map(tuple, variant))
            if key not in seen:
                seen.add(key)
                orientations.append(variant)

    for _ in range(max_attempts):
        oriented = random.choice(orientations)
        h, w = oriented.shape

        r = random.randint(0, rows - h)
        c = random.randint(0, cols - w)

        new_grid = [row[:] for row in grid]
        valid = True

        for i in range(h):
            for j in range(w):
                if oriented[i][j] not in (0, "0"):
                    if new_grid[r + i][c + j] not in ("0", "Ruins"):
                        valid = False
                        break
            if not valid:
                break

        if not valid:
            continue

        for i in range(h):
            for j in range(w):
                if oriented[i][j] not in (0, "0"):
                    new_grid[r + i][c + j] = oriented[i][j]

        ok, _ = validate_placement(grid, new_grid, card, player)
        if ok:
            return new_grid

    return None


def _active_monsters_for_season(monster_deck, drawn_monster_names, season_index):
    unlocked_count = min(len(monster_deck), season_index + 1)
    return [
        card for card in monster_deck[:unlocked_count]
        if card.name not in drawn_monster_names
    ]

def run_single_game(game_id="sim_001", verbose=False):
    session = GameSession(game_id)

    initial = gameStart.build_starting_grid() if hasattr(gameStart, "build_starting_grid") else [["0" for _ in range(11)] for _ in range(11)]
    player = Player("bot", sample_grid=copy.deepcopy(initial))
    player.current_grid = copy.deepcopy(initial)

    session.players[player.id] = player
    session.seating_order = [player.id]

    session.deck, session.monster_deck = gameStart.build_decks()
    session.score_types, session.score_types_names, dummy = gameStart.select_scoring_cards()
    drawn_monster_names = set()

    if verbose:
        print(f"=== Starting Game {game_id} ===")
        print("Scoring cards:", session.score_types_names)

    for season in range(4):
        player.season_index = season
        season_times = [8, 8, 7, 6]
        player.season_time = season_times[season]
        player.deck_index = 0
        active_monsters = _active_monsters_for_season(session.monster_deck, drawn_monster_names, season)
        season_deck, _ = gameStart.build_decks()
        session.deck = season_deck
        session.deck.extend(copy.deepcopy(active_monsters))
        random.shuffle(session.deck)
        session.current_card = session.deck[0]

        if verbose:
            print(f"\n--- Season {season} ---")

        while player.season_time > 0 and player.deck_index < len(session.deck):
            card = session.deck[player.deck_index]
            session.current_card = card

            if card.type == "Monster":
                assign_monster_quadrant(card)
                new_grid = apply_ambush_rules(player.current_grid, card)

                if new_grid is not None:
                    player.current_grid = new_grid

                drawn_monster_names.add(card.name)

                player.deck_index += 1
                player.season_time -= card.cost
                continue

            if card.type == "Ruins":
                player.ruins_required = True
                player.deck_index += 1
                player.season_time -= card.cost
                continue

            card.ruinFlag = getattr(player, "ruins_required", False)

            new_grid = random_sampled_placement(
                player.current_grid,
                card,
                player
            )

            if new_grid is None and card.ruinFlag:
                new_grid = best_riftlands_tile_placement(player.current_grid)

            if new_grid is None:
                if verbose:
                    print("No legal move found. Skipping card.")
                player.deck_index += 1
                if card.ruinFlag:
                    player.ruins_required = False
                continue

            player.current_grid = new_grid
            player.deck_index += 1
            player.season_time -= card.cost

            if card.ruinFlag:
                player.ruins_required = False

            if verbose:
                print(f"Placed {card.name}, cost {card.cost}, time left {player.season_time}")

        score1 = session.score_types[season % 4](player.current_grid)
        score2 = session.score_types[(season + 1) % 4](player.current_grid)
        coins = player.coins
        monsters = -gameStart.monster_penalty(player.current_grid)
        season_total = score1 + score2 + coins + monsters
        player.score += season_total

        if verbose:
            print(f"Season {season} score: {season_total} (Total: {player.score})")

    if verbose:
        print(f"\n=== Final Score: {player.score} ===")

    return player.score

def run_many_games(n=10, verbose=False):
    scores = []
    for i in range(n):
        score = run_single_game(game_id=f"sim_{i}", verbose=verbose)
        scores.append(score)

    avg_score = sum(scores) / len(scores)
    median_score = statistics.median(scores)
    min_score = min(scores)
    max_score = max(scores)
    std_dev = statistics.pstdev(scores)

    summary = {
        "games": n,
        "scores": scores,
        "median": median_score,
        "min": min_score,
        "max": max_score,
        "std_dev": std_dev
    }

    return summary

if __name__ == "__main__":
    results = run_many_games(n=1000, verbose=False)
    print("=== Simulation Summary ===")
    print("Games:", results["games"])
    print("Median:", results["median"])
    print("Min:", results["min"])
    print("Max:", results["max"])
    print("Std Dev:", results["std_dev"])