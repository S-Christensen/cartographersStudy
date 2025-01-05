class terrainCard:
    def __init__(self, name, cost, terrain, shape):
        self.name = name
        self.cost = cost
        self.terrain = terrain
        self.shape = shape

    def __str__(self):
        return f"{self.name}"
