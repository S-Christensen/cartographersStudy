from terrainCard import terrainCard
import random

deck = []
# 2 cost cards:
deck.append(terrainCard("WildwoodGarden", 2, ["Forest", "Farm"], [[0, 1, 1], [1, 0, 0]]))
deck.append(terrainCard("WildwoodCrossroads", 2, ["Forest", "Village"], [[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
deck.append(terrainCard("FrontierDwelling", 2, ["Village", "Farm"], [[1, 1, 1], [0, 1, 0], [0, 1, 0]]))
deck.append(terrainCard("MangroveSwamp", 2, ["Forest", "Water"], [[1, 1, 1], [1, 0, 1]]))
deck.append(terrainCard("HillsideTerrace", 2, ["Farm", "Water"], [[1, 1], [1, 1]]))
deck.append(terrainCard("CoastalEncampment", 2, ["Village", "Water"], [[1, 1, 1], [1, 0, 0]]))

# 1 cost cards:
deck.append(terrainCard("Pasture", 1, ["Farm"], [[[1,0,1]], [[0, 1, 1], [1, 1, 0]]]))
deck.append(terrainCard("Lagoon", 1, ["Water"], [[[0, 1], [1, 0]], [[1, 1, 1], [0, 1, 0]]]))
deck.append(terrainCard("Settlement", 1, ["Village"], [[[1], [1]], [[0, 0, 1], [0, 1, 1], [1, 1, 0]]]))
deck.append(terrainCard("TimberGrove", 1, ["Forest"], [[[1,0], [1,1]], [[1, 0, 1], [1, 0, 1]]]))

# Special + Monster
deck.append(terrainCard("KethrasGate", 0, ["Forest", "Village", "Farm", "Water", "Monster"], [[1]]))

monsterDeck = []
monsterDeck.append(terrainCard("GoblinAttack", 0, ["Monster"], [[1, 0, 0], [0, 1, 0], [0, 0, 1]]))
monsterDeck.append(terrainCard("GnollRaid", 0, ["Monster"], [[1, 1], [1, 0], [1, 1]]))
monsterDeck.append(terrainCard("BugbearAssault", 0, ["Monster"], [[1, 0, 1], [1, 0, 1]]))
monsterDeck.append(terrainCard("KoboldOnslaught", 0, ["Monster"], [[1, 0], [1, 1], [1, 0]]))

#Randomize
random.shuffle(monsterDeck)
deck.append(monsterDeck[0])
random.shuffle(deck)
