from sympy import false

from terrainCard import terrainCard
import scoringCards
import random
import math
import numpy as np

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

def filter_criteria(card, criteria):
    result = [criteria["Misc"]]
    if "farm" in card.shapes[0] or "farm" in card.shapes[1]:
         result.insert(0, [criteria["Blue"]])
    if "forest" in card.shapes[0] or "forest" in card.shapes[1]:
        result.insert(0, [criteria["Green"]])
    if "village" in card.shapes[0] or "village" in card.shapes[1]:
        result.insert(0, [criteria["Red"]])
    return result

def flip_and_rotate(shape):
    shapes = []
    for _ in range(2):  # Two flips (original and flipped)
        for _ in range(4):  # Four rotations (0, 90, 180, 270 degrees)
            shapes.append(shape)
            shape = np.rot90(shape)
        shape = np.fliplr(shape)
    return shapes

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

def place_piece(card, grid, scoretypes, strategy):
    criteria = filter_criteria(card, scoretypes)
    best_position, best_shape = evaluate_position(card, grid, strategy, criteria)
    if best_position:
        x, y = best_position
        for i in range(len(best_shape)):
            for j in range(len(best_shape[0])):
                grid[x+i][y+j] = best_shape[i][j]
        print(f"Placing {card.name} at {best_position}")


def play(strategy):
    deck = []
    # 2 cost cards:
    deck.append(terrainCard("WildwoodGarden", 2, [[[0, "Forest", "Forest"], ["Forest", 0, 0]], [[0, "Farm", "Farm"], ["Farm", 0, 0]]]))
    deck.append(terrainCard("WildwoodCrossroads", 2, [[[0, "Forest", 0], ["Forest", "Forest", "Forest"], [0, "Forest", 0]], [[0, "Village", 0], ["Village", "Village", "Village"], [0, "Village", 0]]]))
    deck.append(terrainCard("FrontierDwelling", 2, [[["Village", "Village", "Village"], [0, "Village", 0], [0, "Village", 0]], [["Farm", "Farm", "Farm"], [0, "Farm", 0], [0, "Farm", 0]]]))
    deck.append(terrainCard("MangroveSwamp", 2, [[["Forest", "Forest", "Forest"], ["Forest", 0, "Forest"]], [["Water", "Water", "Water"], ["Water", 0, "Water"]]]))
    deck.append(terrainCard("HillsideTerrace", 2, [[["Farm", "Farm"], ["Farm", "Farm"]],[["Water", "Water"], ["Water", "Water"]]]))
    deck.append(terrainCard("CoastalEncampment", 2,  [[["Village", "Village", "Village"], ["Village", 0, 0]], [["Water", "Water", "Water"], ["Water", 0, 0]]]))

    # 1 cost cards:
    deck.append(terrainCard("Pasture", 1,  [[["Farm",0,"Farm"]], [[0, "Farm", "Farm"], ["Farm", "Farm", 0]]]))
    deck.append(terrainCard("Lagoon", 1, [[[0, "Water"], ["Water", 0]], [["Water", "Water", "Water"], [0, "Water", 0]]]))
    deck.append(terrainCard("Settlement", 1, [[["Village"], ["Village"]], [[0, 0, "Village"], [0, "Village", "Village"], ["Village", "Village", 0]]]))
    deck.append(terrainCard("TimberGrove", 1,  [[["Forest",0], ["Forest","Forest"]], [["Forest", 0, "Forest"], ["Forest", 0, "Forest"]]]))

    # Special + Monster
    deck.append(terrainCard("KethrasGate", 0, [[["Forest"]], [["Village"]], [["Farm"]], [["Water"]], [["Monster"]]]))

    monsterDeck = []
    monsterDeck.append(terrainCard("GoblinAttack", 0,  [["Monster", 0, 0], [0, "Monster", 0], [0, 0, "Monster"]]))
    monsterDeck.append(terrainCard("GnollRaid", 0, [["Monster", "Monster"], ["Monster", 0], ["Monster", "Monster"]]))
    monsterDeck.append(terrainCard("BugbearAssault", 0, [["Monster", 0, "Monster"], ["Monster", 0, "Monster"]]))
    monsterDeck.append(terrainCard("KoboldOnslaught", 0, [["Monster", 0], ["Monster", "Monster"], ["Monster", 0]]))

    #Randomize
    random.shuffle(monsterDeck)
    season = [0, 8]
    green = [scoringCards.deepwood, scoringCards.sleepyvalley, scoringCards.heartoftheforest, scoringCards.faunlostthicket]
    blue = [scoringCards.ulemswallow, scoringCards.craylund, scoringCards.jorekburg, scoringCards.clawsgravepeaks]
    red = [scoringCards.gnomishcolony, scoringCards.outerenclave, scoringCards.caravansary, scoringCards.traylomonastery]
    misc = [scoringCards.silos, scoringCards.starlitsigil, scoringCards.bandedhills, scoringCards.dwarvenholds]

    scoreTypes = [green[random.randint(0,3)], blue[random.randint(0,3)], red[random.randint(0,3)], misc[random.randint(0,3)]]
    random.shuffle(scoreTypes)

    grid= [[0 for _ in range(11)] for _ in range(11)]
    grid[1][1]="mountain"
    grid[3][8]="mountain"
    grid[5][3]="mountain"
    grid[8][9]="mountain"
    grid[9][5]="mountain"
    score = 0
    coins = 0

    mountain_locations = [(1,1), (3,8), (5,3), (8,9), (9,5)]

    while season[0] < 4:
        index = 0
        deck.append(monsterDeck[season[0]])
        random.shuffle(deck)

        while season[1] > 0:
            season[1] -= deck[index].cost

            # TODO places piece
            # placePiece(deck[index])
            for mountain in mountain_locations:
                y = mountain[0]
                x = mountain[1]
                offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]

                # Check orthogonal neighbors of the mountain
                flag = True
                for dx, dy in offsets:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid):
                        # Check if the mountain has all its orthogonal neighbors filled
                        if grid[nx][ny] == 0:
                            flag = false
                if flag:
                    coins+=1
                    mountain_locations.remove(mountain)

            # TODO if card cost 1, check if coin used or not

            if deck[index] in monsterDeck:
                deck.pop(index)
                index -= 1
            index += 1


        score += scoreTypes[season[0] % 4](grid)
        score += scoreTypes[(season[0]+1) % 4](grid)
        score += coins
        # TODO score -= empty adj to monster

        season[0] += 1
        season[1] = 8-math.ceil(season[0]/2.0)
    return score