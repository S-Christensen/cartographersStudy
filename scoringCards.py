def dfs(grid, row, col, visited, terrain_type):
    stack = [(row, col)]
    cluster = []

    while stack:
        r, c = stack.pop()
        if (r, c) not in visited and grid[r][c] == terrain_type:
            visited.add((r, c))
            cluster.append((r, c))
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                    stack.append((nr, nc))
    return cluster

def faunlostthicket(grid):
    if not grid or not grid[0]:
        return 0

    max_length = 0
    cols = len(grid[0])

    for col in range(cols):
        current_length = 0
        for row in grid:
            if row[col] == "forest":
                current_length += 1
                max_length = max(max_length, current_length)
            else:
                current_length = 0

    return max_length*2

def is_surrounded_by_forest_or_edge(grid, r, c):
    rows = len(grid)
    cols = len(grid[0])
    surroundings = [
        (r - 1, c),  # above
        (r + 1, c),  # below
        (r, c - 1),  # left
        (r, c + 1)  # right
    ]

    for nr, nc in surroundings:
        if 0 <= nr < rows and 0 <= nc < cols:
            if grid[nr][nc] != "forest":
                return False
        else:  # Out of bounds, considered as edge of the map
            continue
    return True

def heartoftheforest(grid):
    count = 0
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == "forest" and is_surrounded_by_forest_or_edge(grid, r, c):
                count += 1
    return count*2

def sleepyvalley(grid):
    def count_forests_in_row(row):
        return row.count("forest")

    row_count = 0

    for row in grid:
        if count_forests_in_row(row) >= 3:
            row_count += 1

    return row_count*4

def is_adjacent_to_village(grid, cluster):
    for r, c in cluster:
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == "village":
                return True
    return False

def deepwood(grid):
    visited = set()
    clusters = []

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if (row, col) not in visited and grid[row][col] == "forest":
                cluster = dfs(grid, row, col, visited, "forest")
                clusters.append(cluster)

    count = 0
    for cluster in clusters:
        if len(cluster) >= 5 and not is_adjacent_to_village(grid, cluster):
            count += 1

    return count*6

def gnomishcolony(grid, terrain_type="village"):
    visited = set()
    clusters = []

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if (row, col) not in visited and grid[row][col] == terrain_type:
                cluster = dfs(grid, row, col, visited, terrain_type)
                clusters.append(cluster)

    count_2x2 = 0
    for cluster in clusters:
        if any(
                (r, c) in cluster and
                (r + 1, c) in cluster and
                (r, c + 1) in cluster and
                (r + 1, c + 1) in cluster
                for r, c in cluster
        ):
            count_2x2 += 1

    return count_2x2*6

def contains_4x1_or_1x4(cluster):
    coordinates_set = set(cluster)
    for r, c in coordinates_set:
        # Check for 4x1 rectangle
        if all((r, c + i) in coordinates_set for i in range(4)):
            return True
        # Check for 1x4 rectangle
        if all((r + i, c) in coordinates_set for i in range(4)):
            return True
    return False

def traylomonastery(grid):
    visited = set()
    clusters = []

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if (row, col) not in visited and grid[row][col] == "village":
                cluster = dfs(grid, row, col, visited, "village")
                clusters.append(cluster)

    count = 0
    for cluster in clusters:
        if contains_4x1_or_1x4(cluster):
            count += 1

    return count*7

def calculate_points(cluster):
    rows = set()
    cols = set()
    for r, c in cluster:
        rows.add(r)
        cols.add(c)
    return len(rows) + len(cols)

def caravansary(grid):
    visited = set()
    clusters = []

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if (row, col) not in visited and grid[row][col] == "village":
                cluster = dfs(grid, row, col, visited, "village")
                clusters.append(cluster)

    max_points = 0

    for cluster in clusters:
        points = calculate_points(cluster)
        if points > max_points:
            max_points = points

    return max_points

def calculate_points_for_empty_adjacent(grid, cluster):
    points = 0
    for r, c in cluster:
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == 0:
                points += 1
    return points

def outerenclave(grid):
    visited = set()
    clusters = []

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if (row, col) not in visited and grid[row][col] == "village":
                cluster = dfs(grid, row, col, visited, "village")
                clusters.append(cluster)

    max_points = 0

    for cluster in clusters:
        points = calculate_points_for_empty_adjacent(grid, cluster)
        if points > max_points:
            max_points = points

    return max_points

def ulemswallow(grid):
    def is_farm(r, c):
        return 0 <= r < len(grid) and 0 <= c < len(grid[0]) and grid[r][c] == "farm"

    def count_adjacent_farms(r, c):
        farm_count = 0
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if is_farm(nr, nc):
                farm_count += 1
        return farm_count

    water_count = 0

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == "water" and count_adjacent_farms(r, c) >= 2:
                water_count += 1

    return water_count*4

def has_mountain_and_farm(grid, cluster):
    mountains = set()
    farms = set()

    for r, c in cluster:
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                if grid[nr][nc] == "mountain":
                    mountains.add((nr, nc))
                if grid[nr][nc] == "farm":
                    farms.add((nr, nc))
    return mountains, farms

def clawsgravepeaks(grid):
    visited = set()
    clusters = []
    mountain_count = 0

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if (row, col) not in visited and grid[row][col] == "water":
                cluster = dfs(grid, row, col, visited, "water")
                clusters.append(cluster)

    for cluster in clusters:
        mountains, farms = has_mountain_and_farm(grid, cluster)
        if farms:
            mountain_count += len(mountains)

    return mountain_count*5

def jorekburg(grid):
    column_count = 0

    for col in range(len(grid[0])):
        farm_count = 0
        water_count = 0
        for row in range(len(grid)):
            if grid[row][col] == "farm":
                farm_count += 1
            elif grid[row][col] == "water":
                water_count += 1
        if farm_count == water_count and farm_count > 0:
            column_count += 1

    return column_count*4

def count_adjacent_water(grid, cluster):
    water_count = 0
    for r, c in cluster:
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == "water":
                water_count += 1
    return water_count

def craylund(grid):
    visited = set()
    clusters = []

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if (row, col) not in visited and grid[row][col] == "farm":
                cluster = dfs(grid, row, col, visited, "farm")
                clusters.append(cluster)

    count = 0
    for cluster in clusters:
        if count_adjacent_water(grid, cluster) >= 3:
            count += 1

    return count*7

def dwarvenholds(grid):
    def is_filled(row):
        return all(cell != 0 for cell in row)

    def contains_mountain(row):
        return "mountain" in row

    rows_count = 0
    cols_count = 0

    for row in grid:
        if is_filled(row) and contains_mountain(row):
            rows_count += 1

    for col in range(len(grid[0])):
        column = [grid[row][col] for row in range(len(grid))]
        if is_filled(column) and contains_mountain(column):
            cols_count += 1

    return 7*(rows_count + cols_count)

def bandedhills(grid):
    terrain_types = {"Forest", "Village", "Farm", "Water", "Monster", "Mountain"}
    row_count = 0

    for row in grid:
        unique_terrains = set(row)
        valid_terrains = unique_terrains.intersection(terrain_types)
        if len(valid_terrains) >= 5:
            row_count += 1

    return row_count*4

def starlitsigil(grid):
    visited = set()
    clusters = []

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if (row, col) not in visited and grid[row][col] == 0:
                cluster = dfs(grid, row, col, visited, 0)
                if len(cluster) == 3:
                    clusters.append(cluster)

    return len(clusters)*4


def silos(grid):
    def is_filled(column):
        return all(cell != 0 for cell in column)

    filled_odd_column_count = 0

    for col in range(0, len(grid[0]), 2):  # Using range to iterate over odd-numbered columns (0-based index)
        column = [grid[row][col] for row in range(len(grid))]
        if is_filled(column):
            filled_odd_column_count += 1

    return filled_odd_column_count*10
