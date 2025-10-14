class terrainCard:
    def __init__(self, name, cost, shape):
        self.name = name
        self.cost = cost
        self.shape = shape
        self.is_ruin = shape == [[[-1]]]

    def __str__(self):
        return f"{self.name}"

    def to_dict(self):
        return {
            "id": self.name,
            "cost": self.cost,
            "shapes": self.shape,
            "terrainOptions": self.get_terrain_types(),
            "isRuin": self.is_ruin
        }

    def get_terrain_types(self):
        types = set()
        for shape_variant in self.shape:
            for row in shape_variant:
                for cell in row:
                    if cell and cell != 0 and cell != -1:
                        types.add(cell)
        return list(types)