import random
import numpy as np
import copy
from gameStart import flip_and_rotate, validate_placement

def random_sampled_placement(grid, card, player, max_attempts=200):
    rows, cols = len(grid), len(grid[0])

    orientations = []
    seen = set()
    for shape in card.shape:
        for variant in flip_and_rotate(np.array(shape)):
            key = tuple(map(tuple, variant))
            if key not in seen:
                seen.add(key)
                orientations.append(variant)

    for _ in range(max_attempts):
        oriented = random.choice(orientations)
        h, w = oriented.shape

        r = random.randint(0, rows - h)
        c = random.randint(0, cols - w)

        new_grid = copy.deepcopy(grid)
        valid = True

        for i in range(h):
            for j in range(w):
                if str(oriented[i][j]) != "0":
                    if new_grid[r+i][c+j] not in ("0", "Ruins"):
                        valid = False
                        break
            if not valid:
                break

        if not valid:
            continue

        for i in range(h):
            for j in range(w):
                if str(oriented[i][j]) != "0":
                    new_grid[r+i][c+j] = oriented[i][j]

        ok, _ = validate_placement(grid, new_grid, card, player)
        if ok:
            return new_grid

    return None