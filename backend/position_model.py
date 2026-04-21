import copy
import random
import statistics
import numpy as np
from multiprocessing import Pool, cpu_count

import gameStart
from gameStart import GameSession, Player, flip_and_rotate
import midgameEvaluation as me
import scoringCards

A_WEIGHTS        = [2, 1, 1, 1]
B_WEIGHTS        = [2, 1, 0, 0]
C_WEIGHTS        = [2, 2, 1, 0]
D_WEIGHTS        = [2, 2, 2, 1]
COIN_WEIGHTS     = [4, 3, 2, 1]
MONSTER_WEIGHTS  = [4, 3, 2, 1]

SEASON_WEIGHTS = {
    season: [
        A_WEIGHTS[season],
        B_WEIGHTS[season],
        C_WEIGHTS[season],
        D_WEIGHTS[season],
        COIN_WEIGHTS[season],
        MONSTER_WEIGHTS[season],
    ]
    for season in range(4)
}

TERRAIN_TYPES = ["Forest", "Village", "Farm", "Water"]
RIFTLANDS_TERRAIN_TYPES = ["Forest", "Village", "Farm", "Water", "Monster"]
MOUNTAIN_LOCATIONS = [(1, 3), (2, 8), (5, 5), (8, 2), (9, 7)]
RUINS_LOCATIONS = [(1, 5), (2, 1), (2, 9), (8, 1), (8, 9), (9, 5)]

TRAINED_POSITION_WEIGHTS = np.array([0.20159549, 0.18746506, 0.21314694, 0.19844468, 0.03967415, 0.15967368])

def init_genetic_weights():
    return np.array([1/6] * 6)
    # return np.array([0.03006665, 0.22801868, 0.26735871, 0.25109238, 0.09937612, 0.12408745])


def mutate_weights(weights, mutation_scale=0.05):
    new = weights + np.random.normal(0, mutation_scale, size=weights.shape)
    new = np.clip(new, 0.0001, None)
    new /= new.sum()
    return new


def crossover_weights(a, b):
    child = (a + b) / 2.0
    child = np.clip(child, 0.0001, None)
    child /= child.sum()
    return child


def random_weights():
    w = np.random.random(6)
    w /= w.sum()
    return w


def build_card_variants(card):
    orientations = []
    seen = set()
    for shape in card.shape:
        # Keep numeric 0 cells as integers; mixed string/int arrays otherwise coerce to strings.
        shape_arr = np.array(shape, dtype=object)
        for variant in flip_and_rotate(shape_arr):
            key = tuple(map(tuple, variant))
            if key not in seen:
                seen.add(key)
                orientations.append(variant)

    first_shape_keys = set()
    for variant in flip_and_rotate(np.array(card.shape[0], dtype=object)):
        first_shape_keys.add(tuple(map(tuple, variant)))

    card.variants = orientations
    card.first_shape_keys = first_shape_keys
    return card


def prepare_deck_variants(deck):
    for card in deck:
        build_card_variants(card)


def build_starting_grid(size=11):
    grid = [["0" for _ in range(size)] for _ in range(size)]
    for r, c in MOUNTAIN_LOCATIONS:
        grid[r][c] = "Mountain"
    for r, c in RUINS_LOCATIONS:
        grid[r][c] = "Ruins"
    return grid


def make_deterministic_game_scenario(seed, include_season_decks=False):
    prev_state = random.getstate()
    random.seed(seed)
    deck, monster_deck = gameStart.build_decks()
    score_types, score_types_names, score_types_colors = gameStart.select_scoring_cards()

    season_decks = []
    if include_season_decks:
        for season in range(4):
            season_deck, _ = gameStart.build_decks()
            prepare_deck_variants(season_deck)
            # Store a deterministic shuffled base season deck (non-monster cards only).
            random.shuffle(season_deck)
            season_decks.append(copy.deepcopy(season_deck))
    random.setstate(prev_state)

    prepare_deck_variants(deck)
    scenario = {
        "seed": seed,
        "deck": deck,
        "monster_deck": monster_deck,
        "score_types": score_types,
        "score_types_names": score_types_names,
        "score_types_colors": score_types_colors,
    }
    if include_season_decks:
        scenario["season_decks"] = season_decks
    return scenario


def _active_monsters_for_season(monster_deck, drawn_monster_names, season_index):
    """Unlock one new monster per season and keep only those not yet drawn."""
    unlocked_count = min(len(monster_deck), season_index + 1)
    return [
        card for card in monster_deck[:unlocked_count]
        if card.name not in drawn_monster_names
    ]


def make_game_scenarios(n, base_seed=0, include_season_decks=False):
    return [make_deterministic_game_scenario(base_seed + i, include_season_decks=include_season_decks) for i in range(n)]


def aggregate_scores(scores, method="median", trim_frac=0.1):
    if not scores:
        return 0.0
    if method == "mean":
        return sum(scores) / len(scores)
    if method == "median":
        return statistics.median(scores)
    if method == "trimmed":
        sorted_scores = sorted(scores)
        trim = int(len(scores) * trim_frac)
        trimmed = sorted_scores[trim: len(scores) - trim] if len(sorted_scores) > 2 * trim else sorted_scores
        return sum(trimmed) / len(trimmed)
    raise ValueError(f"Unknown aggregate method: {method}")


def relative_scores(candidate_scores, baseline_scores):
    return [c - b for c, b in zip(candidate_scores, baseline_scores)]


def evaluate_candidate_scores(weights, scenarios, processes=None):
    return run_many_games(weights, n=len(scenarios), verbose=False, processes=processes, scenarios=scenarios)["scores"]


def best_single_tile_placement(grid, season_index, genetic_weights, reward_fns):
    rows, cols = len(grid), len(grid[0])
    best_score = -1e9
    best_grid = None

    for terrain in TERRAIN_TYPES:
        oriented = np.array([[terrain]], dtype=object)
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] not in ("0", "Ruins"):
                    continue

                new_grid = [row[:] for row in grid]
                new_grid[r][c] = terrain

                action = {
                    "cells": [(r, c)],
                    "terrain": terrain,
                    "player": None,
                    "shape": oriented,
                    "card_cost": 1,
                    "card_name": "Fallback",
                    "is_first_shape": True
                }

                score = evaluate_action(grid, new_grid, action, season_index, genetic_weights, reward_fns)
                if score > best_score:
                    best_score = score
                    best_grid = new_grid

    return best_grid


def best_riftlands_tile_placement(grid, season_index, genetic_weights, reward_fns):
    """Pick the best single-cell Rift Lands terrain on any legal empty/ruins cell."""
    rows, cols = len(grid), len(grid[0])
    best_score = -1e9
    best_grid = None

    for terrain in RIFTLANDS_TERRAIN_TYPES:
        oriented = np.array([[terrain]], dtype=object)
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] not in ("0", "Ruins"):
                    continue

                new_grid = [row[:] for row in grid]
                new_grid[r][c] = terrain

                action = {
                    "cells": [(r, c)],
                    "terrain": terrain,
                    "player": None,
                    "shape": oriented,
                    "card_cost": 0,
                    "card_name": "Rift Lands Fallback",
                    "is_first_shape": True,
                }

                score = evaluate_action(grid, new_grid, action, season_index, genetic_weights, reward_fns)
                if score > best_score:
                    best_score = score
                    best_grid = new_grid

    return best_grid


def is_valid_placement(grid, oriented, r, c, card):
    placed_any = False
    h, w = oriented.shape
    for i in range(h):
        for j in range(w):
            if oriented[i][j] in (0, "0"):
                continue
            cell = grid[r + i][c + j]
            if cell not in ("0", "Ruins"):
                return None
            placed_any = True
            if card.ruinFlag and cell == "Ruins":
                return True

    return not card.ruinFlag and placed_any


def is_first_shape_variant(oriented, card):
    return tuple(map(tuple, oriented)) in card.first_shape_keys


def _safe_reward(name):
    fn = getattr(me, f"{name}_reward", None)
    if fn is None:
        return lambda *args, **kwargs: 0.0
    return fn


PROGRESS_TO_REWARD = {
    scoringCards.greenbough:       _safe_reward("greenbough"),
    scoringCards.stonesideForest:  _safe_reward("stoneside"),
    scoringCards.sentinelWood:     _safe_reward("sentinel"),
    scoringCards.treetower:        _safe_reward("treetower"),

    scoringCards.goldenGranary:    _safe_reward("goldenGranary"),
    scoringCards.shoresideExpanse: _safe_reward("shoreside"),
    scoringCards.canalLake:        _safe_reward("canalLake"),
    scoringCards.magesValley:      _safe_reward("magesValley"),

    scoringCards.greengoldPlains:  _safe_reward("greengoldPlains"),
    scoringCards.shieldgate:       _safe_reward("shieldgate"),
    scoringCards.greatCity:        _safe_reward("greatCity"),
    scoringCards.wildholds:        _safe_reward("wildholds"),

    scoringCards.borderlands:      _safe_reward("borderlands"),
    scoringCards.brokenRoad:       _safe_reward("brokenRoad"),
    scoringCards.cauldrons:        _safe_reward("cauldrons"),
    scoringCards.lostBarony:       _safe_reward("lostBarony"),
}

def coin_reward(prev_grid, curr_grid, action, player):
    bonus = 0
    if action.get("is_first_shape") == True and action.get("card_cost") == 1:
        bonus = 1
    return me.mountain_coin_reward(prev_grid, curr_grid, action) + bonus


def monster_reward(prev_grid, curr_grid, action):
    prev = -gameStart.monster_penalty(prev_grid)
    curr = -gameStart.monster_penalty(curr_grid)
    return curr - prev

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
    return card


def apply_ambush_rules(grid, card):
    """
    Alternative ambush rules:
    - Start from indicated corner
    - Sweep along edge in given direction
    - If no legal placement, move one cell inward and repeat
    - No flips/rotations; use card.shape[0] as-is
    """
    # Preserve int 0 holes so ambush shapes do not collapse to filled rectangles.
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
        start_r, start_c = 0, 0

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

def evaluate_action(prev_grid, curr_grid, action, season_index, genetic_weights, reward_fns):
    season_w = SEASON_WEIGHTS[season_index]
    total_weights = genetic_weights * np.array(season_w)

    total = 0.0

    for w, fn in zip(total_weights, reward_fns):
        if w <= 0:
            continue

        if fn is coin_reward:
            total += w * fn(prev_grid, curr_grid, action, action.get("player"))
        else:
            total += w * fn(prev_grid, curr_grid, action)

    total += me.penalize_surrounded_empty(prev_grid, action)
    return total

def best_scored_placement(grid, card, player, season_index, genetic_weights, reward_fns):
    rows, cols = len(grid), len(grid[0])
    if not hasattr(card, "variants"):
        build_card_variants(card)

    best_score = -1e9
    best_grid = None

    for oriented in card.variants:
        h, w = oriented.shape
        max_positions = (rows - h + 1) * (cols - w + 1)
        if card.ruinFlag:
            # Ruins-constrained turns should be exhaustive so we do not miss a legal ruins placement.
            sampled_positions = {(r, c) for r in range(rows - h + 1) for c in range(cols - w + 1)}
        else:
            num_samples = min(50, max_positions)
            sampled_positions = set()
            while len(sampled_positions) < num_samples:
                r = random.randint(0, rows - h)
                c = random.randint(0, cols - w)
                sampled_positions.add((r, c))

        for r, c in sampled_positions:
                placement = []
                legal = True
                ruins_satisfied = not card.ruinFlag

                for i in range(h):
                    for j in range(w):
                        if oriented[i][j] in (0, "0"):
                            continue
                        cell = grid[r + i][c + j]
                        if cell not in ("0", "Ruins"):
                            legal = False
                            break
                        placement.append((r + i, c + j))
                        if card.ruinFlag and cell == "Ruins":
                            ruins_satisfied = True
                    if not legal:
                        break

                if not legal or not ruins_satisfied or not placement:
                    continue

                new_grid = [row[:] for row in grid]
                for rr, cc in placement:
                    new_grid[rr][cc] = oriented[rr - r][cc - c]

                action = {
                    "cells": placement,
                    "terrain": card.terrainOptions[0] if hasattr(card, "terrainOptions") else None,
                    "player": player,
                    "shape": oriented,
                    "card_cost": card.cost,
                    "card_name": card.name,
                    "is_first_shape": is_first_shape_variant(oriented, card)
                }

                score = evaluate_action(grid, new_grid, action, season_index, genetic_weights, reward_fns)
                if score > best_score:
                    best_score = score
                    best_grid = new_grid

    if best_grid is None:
        return best_single_tile_placement(grid, season_index, genetic_weights, reward_fns)

    return best_grid

def run_single_game(weights, game_id="sim_genetic", verbose=False, scenario=None, trace=False):
    session = GameSession(game_id)

    initial = build_starting_grid()
    player = Player("bot", sample_grid=copy.deepcopy(initial))
    player.current_grid = copy.deepcopy(initial)

    session.players[player.id] = player
    session.seating_order = [player.id]

    if scenario is None:
        session.deck, session.monster_deck = gameStart.build_decks()
        prepare_deck_variants(session.deck)
        session.score_types, session.score_types_names, DUMMY = gameStart.select_scoring_cards()
    else:
        session.deck = copy.deepcopy(scenario["deck"])
        session.monster_deck = copy.deepcopy(scenario["monster_deck"])
        session.score_types = scenario["score_types"]
        session.score_types_names = scenario["score_types_names"]
        DUMMY = None

    session.current_card = session.deck[0] if session.deck else None

    if verbose:
        print(f"=== Starting Game {game_id} ===")
        print("Scoring cards:", session.score_types_names)

    trace_log = []
    drawn_monster_names = set()

    def record_trace(season, turn_index, card, move_type, grid_before, grid_after, time_before, time_after):
        if not trace:
            return
        trace_log.append({
            "season": season,
            "turn_index": turn_index,
            "move_type": move_type,
            "card": card.to_dict() if hasattr(card, "to_dict") else card,
            "grid_before": copy.deepcopy(grid_before),
            "grid_after": copy.deepcopy(grid_after),
            "placement_diff": gameStart.get_placement_diff(grid_before, grid_after).tolist(),
            "coins_before": player.coins,
            "coins_after": player.coins,
            "season_time_before": time_before,
            "season_time_after": time_after,
        })

    for season in range(4):
        player.season_index = season
        season_times = [8, 8, 7, 6]
        player.season_time = season_times[season]
        player.deck_index = 0
        active_monsters = _active_monsters_for_season(session.monster_deck, drawn_monster_names, season)

        if scenario is not None and scenario.get("season_decks"):
            # Scenario decks are deterministic base decks; append currently active monsters.
            base_deck = [
                card for card in copy.deepcopy(scenario["season_decks"][season])
                if card.type != "Monster"
            ]
            session.deck = base_deck + copy.deepcopy(active_monsters)
            # Keep scenario runs reproducible while still allowing monsters to appear anywhere.
            scenario_seed = int(scenario.get("seed", 0))
            rng = random.Random(scenario_seed * 100 + season)
            rng.shuffle(session.deck)
        else:
            session.deck, _ = gameStart.build_decks()
            session.deck.extend(copy.deepcopy(active_monsters))
            random.shuffle(session.deck)

        scoring_fns = session.score_types
        reward_fns = [PROGRESS_TO_REWARD.get(fn, lambda *a, **k: 0.0) for fn in scoring_fns]
        reward_fns += [coin_reward, monster_reward]

        if verbose:
            print(f"\n--- Season {season} ---")

        while player.season_time > 0 and player.deck_index < len(session.deck):
            card = session.deck[player.deck_index]
            session.current_card = card
            time_before = player.season_time
            grid_before = copy.deepcopy(player.current_grid)

            if card.type == "Monster":
                drawn_monster_names.add(card.name)
                assign_monster_quadrant(card)
                new_grid = apply_ambush_rules(player.current_grid, card)

                if new_grid is not None:
                    player.current_grid = new_grid

                record_trace(season, player.deck_index, card, "monster", grid_before, player.current_grid, time_before, player.season_time - card.cost)

                player.deck_index += 1
                player.season_time -= card.cost
                continue

            if card.type == "Ruins":
                # Ruins cards do not place a tile; they constrain the next standard card.
                player.ruins_required = True
                record_trace(season, player.deck_index, card, "ruins", grid_before, player.current_grid, time_before, player.season_time - card.cost)
                player.deck_index += 1
                player.season_time -= card.cost
                continue

            card.ruinFlag = player.ruins_required

            new_grid = best_scored_placement(
                player.current_grid,
                card,
                player,
                season,
                weights,
                reward_fns
            )

            if new_grid is None and player.ruins_required:
                # Official fallback for blocked ruins turn: place one Rift Lands cell anywhere legal.
                new_grid = best_riftlands_tile_placement(player.current_grid, season, weights, reward_fns)

            if new_grid is None:
                if verbose:
                    print("No legal move found. Skipping card.")
                record_trace(season, player.deck_index, card, "skip", grid_before, player.current_grid, time_before, player.season_time)
                if player.ruins_required:
                    player.ruins_required = False
                player.deck_index += 1
                continue

            player.current_grid = new_grid
            record_trace(season, player.deck_index, card, "placement", grid_before, player.current_grid, time_before, player.season_time - card.cost)
            if player.ruins_required:
                player.ruins_required = False
            player.deck_index += 1
            player.season_time -= card.cost

            if verbose:
                print(f"Placed {card.name}, cost {card.cost}, time left {player.season_time}")

        score_func_1 = session.score_types[player.season_index % 4]
        score_func_2 = session.score_types[(player.season_index + 1) % 4]

        grid = player.current_grid
        score1 = score_func_1(grid)
        score2 = score_func_2(grid)
        coins = player.coins
        monsters = -gameStart.monster_penalty(grid)

        season_total = score1 + score2 + coins + monsters
        player.score += season_total

        if verbose:
            print(f"Season {season} score: {season_total} (Total: {player.score})")

    if verbose:
        print(f"\n=== Final Score: {player.score} ===")

    if trace:
        return {"score": player.score, "trace": trace_log}
    return player.score

def run_many_games(weights, n=100, verbose=False, processes=None, scenarios=None, base_seed=0):
    if processes is None:
        processes = max(1, cpu_count() - 1)

    if scenarios is None:
        scenarios = make_game_scenarios(n, base_seed=base_seed)

    if verbose or processes == 1:
        scores = [run_single_game(weights, game_id=f"sim_{i}", verbose=verbose, scenario=scenarios[i]) for i in range(n)]
    else:
        jobs = [(weights, f"sim_{i}", False, scenarios[i]) for i in range(n)]
        with Pool(processes=processes) as pool:
            scores = pool.starmap(run_single_game, jobs)

    median_score = statistics.median(scores)
    min_score = min(scores)
    max_score = max(scores)
    std_dev = statistics.pstdev(scores)

    return {
        "games": n,
        "scores": scores,
        "median": median_score,
        "min": min_score,
        "max": max_score,
        "std_dev": std_dev
    }

def evolve_weights(parent, generations=100, population=24, mutation_scale=0.08, min_mutation_scale=0.02, mutation_decay=0.95, games_per_eval=120, processes=None, preliminary_games=None, recheck_top=6, aggregate_method="median"):
    if preliminary_games is None:
        preliminary_games = max(1, games_per_eval // 2)
    extra_games = games_per_eval - preliminary_games

    for gen in range(generations):
        effective_mutation_scale = max(min_mutation_scale, mutation_scale * (mutation_decay ** gen))

        # Build candidate pool using mutation, crossover, and occasional random exploration
        num_mutants = max(1, int((population - 1) * 0.5))
        num_cross = max(1, (population - 1) - num_mutants)

        mutants = [mutate_weights(parent, effective_mutation_scale) for _ in range(num_mutants)]
        crosses = [crossover_weights(parent, random_weights()) for _ in range(num_cross)]

        candidates = [parent] + mutants + crosses
        candidates = candidates[:population]
        while len(candidates) < population:
            candidates.append(random_weights())

        if gen > 0 and gen % 5 == 0:
            # Inject additional random candidate to escape local optima
            candidates[-1] = random_weights()

        # keep scenario collection deterministic for comparability
        prelim_scenarios = make_game_scenarios(preliminary_games, base_seed=42)
        parent_prelim_scores = evaluate_candidate_scores(parent, prelim_scenarios, processes=processes)

        candidate_prelim_scores = [parent_prelim_scores]
        for w in candidates[1:]:
            candidate_prelim_scores.append(evaluate_candidate_scores(w, prelim_scenarios, processes=processes))

        candidate_fitness = []
        for scores in candidate_prelim_scores:
            rel = relative_scores(scores, parent_prelim_scores)
            fitness = aggregate_scores(rel, method=aggregate_method)
            median_score = aggregate_scores(scores, method="median")
            candidate_fitness.append((fitness, median_score))

        # parent_median will be set later based on full scores

        ranked = sorted(
            enumerate(candidate_fitness),
            key=lambda item: (item[1][0], item[1][1]),
            reverse=True
        )

        selected = [index for index, _ in ranked[:recheck_top]]
        if 0 not in selected:
            selected.append(0)

        if extra_games > 0:
            extra_scenarios = make_game_scenarios(extra_games, base_seed=gen * 1000 + 1000)
            parent_extra_scores = evaluate_candidate_scores(parent, extra_scenarios, processes=processes)
            parent_full_scores = parent_prelim_scores + parent_extra_scores

            final_results = []
            for index in selected:
                if index == 0:
                    candidate_full_scores = parent_full_scores
                else:
                    candidate_extra_scores = evaluate_candidate_scores(candidates[index], extra_scenarios, processes=processes)
                    candidate_full_scores = candidate_prelim_scores[index] + candidate_extra_scores

                rel_full = relative_scores(candidate_full_scores, parent_full_scores)
                fitness = aggregate_scores(rel_full, method=aggregate_method)
                median_score = aggregate_scores(candidate_full_scores, method="median")
                final_results.append((fitness, median_score, candidates[index]))

            final_results.sort(key=lambda x: (x[0], x[1]), reverse=True)
            best_fitness, best_median, best_weights = final_results[0]
            parent_median = aggregate_scores(parent_full_scores, method="median")
        else:
            best_fitness, best_median = candidate_fitness[selected[0]]
            best_weights = candidates[selected[0]]
            parent_median = candidate_fitness[0][1]

        improvement = best_median - parent_median
        accepted_weights = best_weights
        if best_median <= parent_median:
            accepted_weights = parent
            if best_median < parent_median:
                print(f"Generation {gen}: no improvement, keeping parent. parent_median={parent_median:.2f}, best_median={best_median:.2f}, mutation_scale={effective_mutation_scale:.5f}")
            else:
                print(f"Generation {gen}: tie with parent. parent_median={parent_median:.2f}, best_median={best_median:.2f}, mutation_scale={effective_mutation_scale:.5f}")
        else:
            print(f"Generation {gen}: parent_median={parent_median:.2f}, best_median={best_median:.2f}, improvement={improvement:.2f}, fitness={best_fitness:.4f}, mutation_scale={effective_mutation_scale:.5f}, best_weights={best_weights}")

        parent = accepted_weights

    return parent

if __name__ == "__main__":
    print("=== Baseline with equal weights (1/6 each) ===")
    w0 = init_genetic_weights()
    
    baseline_results = run_many_games(w0, n=5000, verbose=False)
    print("Games:", baseline_results["games"])
    print("Median:", baseline_results["median"])
    print("Min:", baseline_results["min"])
    print("Max:", baseline_results["max"])
    print("Std Dev:", baseline_results["std_dev"])
    '''
    
    print("\n=== Starting genetic evolution ===")
    best = evolve_weights(w0, generations=25, population=15, mutation_scale=0.10, min_mutation_scale=0.03, mutation_decay=0.97, games_per_eval=100, processes=None, preliminary_games=None, recheck_top=6, aggregate_method="median")
    print("\n=== Middle evolved weights ===")
    print(best)

    baseline_results = run_many_games(best, n=100, verbose=False)
    print("Games:", baseline_results["games"])
    print("Median:", baseline_results["median"])
    print("Min:", baseline_results["min"])
    print("Max:", baseline_results["max"])
    print("Std Dev:", baseline_results["std_dev"])

    best = evolve_weights(best, generations=20, population=15, mutation_scale=0.05, min_mutation_scale=0.01, mutation_decay=0.95, games_per_eval=100, processes=None, preliminary_games=None, recheck_top=4, aggregate_method="median")
    print("\n=== Final evolved weights ===")
    print(best)
    '''
    best = TRAINED_POSITION_WEIGHTS
    print("\n=== Evaluating evolved weights ===")
    final_results = run_many_games(best, n=5000, verbose=False)
    print("Games:", final_results["games"])
    print("Median:", final_results["median"])
    print("Min:", final_results["min"])
    print("Max:", final_results["max"])
    print("Std Dev:", final_results["std_dev"])