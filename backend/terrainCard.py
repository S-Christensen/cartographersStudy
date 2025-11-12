class terrainCard:
    def __init__(self, name, cost, shape, cardType):
        self.name = name
        self.cost = cost
        self.shape = shape
        self.type = cardType
        self.ruinFlag = False #Indicates if card needs to be set on ruin (used for persistent player data)

    def __str__(self):
        return f"{self.name}"

    def to_dict(self):
        return {
            "id": self.name,
            "cost": self.cost,
            "shape": self.shape,
            "terrainOptions": self.get_terrain_types(),
            "type": self.type,
            "ruinFlag": self.flag
        }

    def get_terrain_types(self):
        types = set()
        for shape_variant in self.shape:
            for row in shape_variant:
                for cell in row:
                    if cell and cell != 0 and cell != -1:
                        types.add(cell)
        return list(types)