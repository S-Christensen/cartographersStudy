class terrainCard:
    def __init__(self, name, cost, shape):
        self.name = name
        self.cost = cost
        self.shape = shape

    def __str__(self):
        return f"{self.name}"
