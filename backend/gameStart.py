from terrainCard import terrainCard
import scoringCards
import random
import math
import numpy as np
import copy

class Player:
    def __init__(self, player_id, sample_grid):
        self.id = player_id
        self.grid_history = []
        self.current_grid = sample_grid
        self.score = 0
        self.coins = 0
        self.flags = {
            "placed_this_turn": False,
            "used_coin_bonus": False,
        }
        self.mountain_locations = [(1, 3), (2, 8), (5, 5), (8, 2), (9, 7)]


class GameSession:
    def __init__(self, session_id):
        self.id = session_id
        self.players = {}
        self.deck, self.monster_deck = build_decks()
        self.score_types, self.score_types_names = select_scoring_cards()
        self.current_card = self.deck[0]
        self.season_time = 8
        self.deck_index = 0
        self.season_index = 0
        self.season_initialized = False

def check_orthogonal_neighbors(grid, x, y):
    # Dimensions of the grid
    rows = len(grid)
    cols = len(grid[0])

    # Offsets to check the orthogonal neighbors (up, down, left, right)
    offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # Check orthogonal neighbors of the placed piece
    for dx, dy in offsets:
        nx, ny = x + dx, y + dy
        if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == "mountain":
            # Check if the mountain has all its orthogonal neighbors filled
            for dx_m, dy_m in offsets:
                mx, my = nx + dx_m, ny + dy_m
                if 0 <= mx < rows and 0 <= my < cols:
                    if grid[mx][my] != "filled" and grid[mx][my] != "mountain":
                        return False
                else:
                    return False
    return True

'''
def filter_criteria(card, criteria):
    result = [criteria["Misc"]]
    if "farm" in card.shapes[0] or "farm" in card.shapes[1]:
         result.insert(0, [criteria["Blue"]])
    if "forest" in card.shapes[0] or "forest" in card.shapes[1]:
        result.insert(0, [criteria["Green"]])
    if "village" in card.shapes[0] or "village" in card.shapes[1]:
        result.insert(0, [criteria["Red"]])
    return result
'''

def flip_and_rotate(shape):
    shapes = []
    for flip in [False, True]:
        flipped = np.fliplr(shape) if flip else shape
        for k in range(4):  # Rotations: 0, 90, 180, 270
            rotated = np.rot90(flipped, k)
            shapes.append(rotated)
    return shapes

'''
def evaluate_position(card, grid, weights, criteria):
    best_score = -1
    best_position = None
    best_shape = None
    for shape in card.shapes:
        for variant in flip_and_rotate(shape):
            variant = np.array(variant)
            for x in range(len(grid) - len(variant) + 1):
                for y in range(len(grid[0]) - len(variant[0]) + 1):
                    score = 0
                    for criterion in criteria:
                        # Placeholder for actual scoring logic
                        score += criterion() * weights
                    if score > best_score:
                        best_score = score
                        best_position = (x, y)
                        best_shape = variant
    return best_position, best_shape
'''
'''
def place_piece(card, grid, scoretypes, strategy):
    criteria = filter_criteria(card, scoretypes)
    best_position, best_shape = evaluate_position(card, grid, strategy, criteria)
    if best_position:
        x, y = best_position
        for i in range(len(best_shape)):
            for j in range(len(best_shape[0])):
                grid[x+i][y+j] = best_shape[i][j]
        print(f"Placing {card.name} at {best_position}")
'''
# TODO drag into the grid and rotate/flip while dragging using keybinds
# q = left rotate, e = right rotate, f = flip

def get_placement_diff(prev_grid, new_grid):
    
    prev_grid = np.array(prev_grid, dtype=str)
    new_grid = np.array(new_grid, dtype=str)
    print("Previous Grid:\n", prev_grid)
    print("New Grid:\n", new_grid)


    # Make a grid that shows only newly placed terrain (everything else "0")
    diff_grid = np.where(((prev_grid == "0") | (prev_grid == "Ruins")) & (new_grid != "0"), new_grid, "0")
    return diff_grid

def normalize_diff(arr):
    arr = np.array(arr, dtype=object)

    # If the array is empty, return an empty 2D array
    if arr.size == 0:
        return np.empty((0, 0), dtype=object)

    # Find indices where entries are not "0"
    non_zero_indices = np.argwhere(arr != "0")
    if non_zero_indices.size == 0:
        return np.empty((0, 0), dtype=object)

    min_x, min_y = non_zero_indices.min(axis=0)
    max_x, max_y = non_zero_indices.max(axis=0)

    cropped = arr[min_x:max_x + 1, min_y:max_y + 1]

    # Ensure result is 2D (NumPy collapses 1D slices)
    if cropped.ndim == 1:
        cropped = cropped[np.newaxis, :]  # make it 2D row
    elif cropped.ndim == 0:
        cropped = cropped.reshape((1, 1))

    return cropped

def matches_card_shape(diff, card, player):
    print("Diff:\n", diff)
    placed_shape = normalize_diff(diff)
    placed_mask = (placed_shape != '0')
    print("Placed Shape:\n", placed_shape)
    print("Placed Mask:\n", placed_mask)

    for shape in card.shape:
        for variant in flip_and_rotate(shape):
            variant = np.array(variant)
            variant_mask = (variant != '0')

            h_diff = placed_shape.shape[0] - variant.shape[0]
            w_diff = placed_shape.shape[1] - variant.shape[1]

            if h_diff < 0 or w_diff < 0:
                continue  # Variant is larger than diff region

            for i in range(h_diff + 1):
                for j in range(w_diff + 1):
                    subregion = placed_shape[i:i+variant.shape[0], j:j+variant.shape[1]]
                    sub_mask = placed_mask[i:i+variant.shape[0], j:j+variant.shape[1]]

                    if np.array_equal(sub_mask, variant_mask) and np.all(subregion[variant_mask] == variant[variant_mask]):
                        if ((card.cost == 1) and (shape == card.shape[0])):
                            player.coins += 1
                        return True
    return False

def placed_on_ruins(diff, ruins_locations=None):
    if ruins_locations is None:
        ruins_locations = [(1, 5), (2, 1), (2, 8), (8, 1), (8, 9), (9, 5)]
    return any((x, y) in ruins_locations for x, y, _ in diff)

def validate_placement(prev_grid, new_grid, card, player):
    diff = get_placement_diff(prev_grid, new_grid)
    if not diff.any():
        return False, "No placement detected"

    if not matches_card_shape(diff, card, player):
        return False, "Shape does not match card"

    if card.ruinFlag and not placed_on_ruins(diff):
        return False, "Ruins card must be placed on a ruins tile"

    return True, "Valid placement"

def get_player_submission(player):
    # TODO: Replace with actual frontend or peer input
    return player.current_grid

def reject_submission(player_id, message):
    #TODO incorporate this with webapp
    print(f"Player {player_id} submission rejected: {message}")

def monster_penalty(grid):
    penalized = set()

    for x in range(len(grid)):
        for y in range(len(grid[0])):
            if grid[x][y] == "Monster":
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if (
                            len(grid) > nx >= 0 == grid[nx][ny] and
                            0 <= ny < len(grid[0])
                    ):
                        penalized.add((nx, ny))

    return len(penalized)

def start():
    game_session = initialize_session()
    deck, monster_deck = build_decks()
    score_types, score_types_names = select_scoring_cards()

    for season_index in range(4):
        run_season(
            game_session,
            deck,
            monster_deck,
            score_types,
            score_types_names,
            season_index,
        )


def initialize_session():
    session = GameSession("session_001")
    session.players["player_1"] = Player("player_1")
    #TODO add scalability using webapp
    return session


def build_decks():
    deck = [
        terrainCard("Treetop Village", 2, [[[0, 0, "Forest", "Forest"], ["Forest", "Forest", "Forest", 0]],
                                          [[0, 0, "Village", "Village"], ["Village", "Village", "Village", 0]]], "Standard"),
        terrainCard("Fishing Village", 2, [[["Village", "Village", "Village", "Village"]],
                                          [["Water", "Water", "Water", "Water"]]], "Standard"),
        terrainCard("Hinterland Stream", 2, [[["Farm", "Farm", "Farm"], ["Farm", 0, 0], ["Farm", 0, 0]],
                                            [["Water", "Water", "Water"], ["Water", 0, 0], ["Water", 0, 0]]], "Standard"),
        terrainCard("Orchard", 2, [[[0, 0, "Forest"], ["Forest", "Forest", "Forest"]],
                                   [[0, 0, "Farm"], ["Farm", "Farm", "Farm"]]], "Standard"),
        terrainCard("Marshlands", 2, [[["Forest", 0, 0], ["Forest", "Forest", "Forest"], ["Forest", 0, 0]],
                                      [["Water", 0, 0], ["Water", "Water", "Water"], ["Water", 0, 0]]], "Standard"),
        terrainCard("Homestead", 2, [[[0, "Village", 0], ["Village", "Village", "Village"]],
                                     [[0, "Farm", 0], ["Farm", "Farm", "Farm"]]], "Standard"),
        terrainCard("Farmland", 1, [[["Farm", "Farm"]],
                                    [[0, "Farm", 0], ["Farm", "Farm", "Farm"], [0, "Farm", 0]]], "Standard"),
        terrainCard("Forgotten Forest", 1, [[["Forest", 0], [0, "Forest"]],
                                           [["Forest", "Forest", 0], [0, "Forest", "Forest"]]], "Standard"),
        terrainCard("Great River", 1, [[["Water", "Water", "Water"]],
                                      [[0, 0, "Water"], [0, "Water", "Water"], ["Water", "Water", 0]]], "Standard"),
        terrainCard("Hamlet", 1, [[["Village", 0], ["Village", "Village"]],
                                  [["Village", "Village", "Village"], ["Village", "Village", 0]]], "Standard"),
        terrainCard("Rift Lands", 0, [[["Forest"]], [["Village"]], [["Farm"]], [["Water"]], [["Monster"]]], "Standard"),
        terrainCard("Temple Ruins", 0, [[[-1]]], "Ruins"),
        terrainCard("Outpost Ruins", 0, [[[-1]]], "Ruins")
    ]

    monster_deck = [
        terrainCard("Goblin Attack", 0, [[["Monster", 0, 0], [0, "Monster", 0], [0, 0, "Monster"]]], "Monster"),
        terrainCard("Gnoll Raid", 0, [[["Monster", "Monster"], ["Monster", 0], ["Monster", "Monster"]]], "Monster"),
        terrainCard("Bugbear Assault", 0, [[["Monster", 0, "Monster"], ["Monster", 0, "Monster"]]], "Monster"),
        terrainCard("Kobold Onslaught", 0, [[["Monster", 0], ["Monster", "Monster"], ["Monster", 0]]], "Monster")
    ]

    random.shuffle(monster_deck)
    return deck, monster_deck


def select_scoring_cards():
    green = [scoringCards.greenbough, scoringCards.stonesideForest, scoringCards.sentinelWood, scoringCards.treetower]
    blue = [scoringCards.goldenGranary, scoringCards.shoresideExpanse, scoringCards.canalLake, scoringCards.magesValley]
    red = [scoringCards.greengoldPlains, scoringCards.shieldgate, scoringCards.greatCity, scoringCards.wildholds]
    misc = [scoringCards.borderlands, scoringCards.brokenRoad, scoringCards.cauldrons, scoringCards.lostBarony]

    score_types = [random.choice(green), random.choice(blue), random.choice(red), random.choice(misc)]
    random.shuffle(score_types)
    score_types_names = []
    for score in score_types:
        score_types_names.append(score.__name__)
    return score_types, score_types_names

def run_season(game_session, deck, monster_deck, score_types, season_index):
    season_time = 8 - math.ceil((season_index + 1) / 2.0)
    deck.append(monster_deck[season_index])
    random.shuffle(deck)
    index = 0
    mountain_locations = [(1, 3), (2, 8), (5, 5), (8, 2), (9, 7)]

    while season_time > 0:
        ruins_flag = False
        card = deck[index]
        season_time -= card.cost
        if card.name in ["TempleRuins", "OutpostRuins"]:
            ruins_flag = True
            index+=1
            card = deck[index]


        # TODO wait for valid input from all players. Maybe set a flag that validate_placement grants?
        # Can't implement this now otherwise test will break lol
        for player in game_session.players.values():
            prev_grid = player.current_grid
            new_grid = get_player_submission(player)
            valid, message = validate_placement(prev_grid, new_grid, card, ruins_flag)
            if not valid:
                reject_submission(player.id, message)
                continue

            player.grid_history.append(copy.deepcopy(prev_grid))
            player.current_grid = new_grid
            player.flags["placed_this_turn"] = True
        # TODO wait for valid input from all players. Maybe set a flag that validate_placement grants?

            for mountain in mountain_locations[:]:
                y, x = mountain
                if check_orthogonal_neighbors(player.current_grid, y, x):
                    player.coins += 1
                    mountain_locations.remove(mountain)

            if player.flags["used_coin_bonus"]:
                player.coins += 1

        if card.name in [m.name for m in monster_deck]:
            deck.pop(index)
            index -= 1
        index += 1

    for player in game_session.players.values():
        player.score += score_types[season_index % 4](player.current_grid)
        player.score += score_types[(season_index + 1) % 4](player.current_grid)
        player.score += player.coins
        player.score -= monster_penalty(player.current_grid)