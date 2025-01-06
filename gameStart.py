from terrainCard import terrainCard
import scoringCards
import random
import math

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

while season[0] < 4:
    index = 0
    deck.append(monsterDeck[season[0]])
    random.shuffle(deck)

    while season[1] > 0:
        season[1] -= deck[index].cost
        if deck[index] in monsterDeck:
            deck.pop(index)
            index -= 1
        index += 1
        # TODO AI places piece
        # TODO if piece adj to mountain, check if coin
        # TODO if card cost 1, check if coin used or not


    score += scoreTypes[season[0] % 4](grid)
    score += scoreTypes[(season[0]+1) % 4](grid)
    score += coins
    # TODO score -= empty adj to monster

    season[0] += 1
    season[1] = 8-math.ceil(season[0]/2.0)

