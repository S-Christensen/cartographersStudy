import copy
import random
import statistics
import numpy as np
import gameStart
from gameStart import GameSession, Player, validate_placement, flip_and_rotate

def random_sampled_placement(grid, card, player, max_attempts=200):
    rows, cols = len(grid), len(grid[0])

    orientations = []
    seen = set()
    for shape in card.shape:
        for variant in flip_and_rotate(np.array(shape)):
            key = tuple(map(tuple, variant))
            if key not in seen:
                seen.add(key)
                orientations.append(variant)

    for _ in range(max_attempts):
        oriented = random.choice(orientations)
        h, w = oriented.shape

        r = random.randint(0, rows - h)
        c = random.randint(0, cols - w)

        new_grid = copy.deepcopy(grid)
        valid = True

        for i in range(h):
            for j in range(w):
                if str(oriented[i][j]) != "0":
                    if new_grid[r+i][c+j] not in ("0", "Ruins"):
                        valid = False
                        break
            if not valid:
                break

        if not valid:
            continue

        for i in range(h):
            for j in range(w):
                if str(oriented[i][j]) != "0":
                    new_grid[r+i][c+j] = oriented[i][j]

        ok, _ = validate_placement(grid, new_grid, card, player)
        if ok:
            return new_grid

    return None

def run_single_game(game_id="sim_001", verbose=False):
    session = GameSession(game_id)
    player = Player("bot", sample_grid=session.players.get("dummy", None) or
                    [["0" for _ in range(11)] for _ in range(11)])

    player.current_grid = copy.deepcopy(session.players.get("dummy", None) or
                                        [["0" for _ in range(11)] for _ in range(11)])

    session.players[player.id] = player
    session.seating_order = [player.id]

    session.deck, session.monster_deck = gameStart.build_decks()
    session.score_types, session.score_types_names = gameStart.select_scoring_cards()
    session.current_card = session.deck[0]

    if verbose:
        print(f"=== Starting Game {game_id} ===")
        print("Scoring cards:", session.score_types_names)

    for season in range(4):
        player.season_index = season
        season_times = [8, 8, 7, 6]
        player.season_time = season_times[season]
        player.deck_index = 0

        if verbose:
            print(f"\n--- Season {season} ---")

        while player.season_time > 0 and player.deck_index < len(session.deck):
            card = session.deck[player.deck_index]
            session.current_card = card

            new_grid = random_sampled_placement(
                player.current_grid,
                card,
                player
            )

            if new_grid is None:
                if verbose:
                    print("No legal move found. Skipping card.")
                player.deck_index += 1
                continue

            player.current_grid = new_grid
            player.deck_index += 1
            player.season_time -= card.cost

            if verbose:
                print(f"Placed {card.name}, cost {card.cost}, time left {player.season_time}")

        score1 = session.score_types[season % 4](player.current_grid)
        score2 = session.score_types[(season + 1) % 4](player.current_grid)
        coins = player.coins
        monsters = -gameStart.monster_penalty(player.current_grid)
        season_total = score1 + score2 + coins + monsters
        player.score += season_total

        # (Optional) Log season result
        # log_season_result(...)

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
    min_score = min(scores)
    max_score = max(scores)
    std_dev = statistics.pstdev(scores)

    summary = {
        "games": n,
        "scores": scores,
        "average": avg_score,
        "min": min_score,
        "max": max_score,
        "std_dev": std_dev
    }

    return summary

if __name__ == "__main__":
    results = run_many_games(n=20, verbose=False)
    print("=== Simulation Summary ===")
    print("Games:", results["games"])
    print("Scores:", results["scores"])
    print("Average:", results["average"])
    print("Min:", results["min"])
    print("Max:", results["max"])
    print("Std Dev:", results["std_dev"])