class terrainCard:
    def __init__(self, name, cost, shape):
        self.name = name
        self.cost = cost
        self.shape = shape
        self.is_ruin = shape == [[[-1]]]

    def __str__(self):
        return f"{self.name}"
