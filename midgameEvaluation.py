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

# Earn 2 points for each forest space in the longest unbroken column of forest spaces
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
    outcome = 0
    for nr, nc in surroundings:
        if 0 <= nr < rows and 0 <= nc < cols:
            if grid[nr][nc] == "forest":
                outcome+=1
        else:  # Out of bounds, considered as edge of the map
            outcome += 1
            continue
    return outcome

# Earn 2 points for each forest space surrounded on all four sides by forest spaces or the edge of the map
def heartoftheforest(grid):
    count = 0.0
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == "forest":
                count += is_surrounded_by_forest_or_edge(grid, r, c)/4
    return count*2

# Earn 4 points for each row that contains three or more forest spaces
def sleepyvalley(grid, current_rows):
    row_count = 0
    straggler = 0

    for row in grid:
        if row.count("forest") >= 3:
            row_count += 1
        else:
            row_count += (row.count("forest")/3)

    return row_count*4

def is_adjacent_to_village(grid, cluster):
    for r, c in cluster:
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == "village":
                return True
    return False

# Earn 6 points for each cluster of five or more forest spaces not adjacent to any village spaces
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
        elif not is_adjacent_to_village(grid, cluster):
            count+=len(cluster)/5

    return count*6

# Earn 6 points for each cluster of village spaces that contains four spaces in a 2x2 square
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
        else:
            champ = 0
            for r,c in cluster:
                temp_count = .25
                if (r + 1, c) in cluster:
                    temp_count+=.25
                if (r, c + 1) in cluster:
                    temp_count+=.25
                if (r + 1, c + 1) in cluster:
                    temp_count+=.25
                champ = max(champ, temp_count)
            count_2x2 += champ

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

# Earn 7 points for each cluster of village spaces that contain 4 spaces in a 4x1 or 1x4 rectangle
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
        else:
            champ = 0
            for r, c in set(cluster):
                # Check for 4x1 rectangle
                i=0
                while (r, c + i) in set(cluster) == "village":
                    i+=1
                # Check for 1x4 rectangle
                j=0
                if (r + j, c) in set(cluster) == "village":
                    j+=1
                champ = max(champ, i/4, j/4)
            count += champ
    return count*7

def calculate_points(cluster):
    rows = set()
    cols = set()
    for r, c in cluster:
        rows.add(r)
        cols.add(c)
    return len(rows) + len(cols)

# Find the cluster of village spaces that will give you the most points where you get 1 point for each row and column
# that contains a space from that cluster
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

# C# Find the cluster of village spaces that will give you the most points where you get 1 point for each empty space
# adjacent to that cluster
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

# Earn 4 points for each water space adjacent to two or more farm spaces
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
            temp = count_adjacent_farms(r, c)
            if grid[r][c] == "water" and temp >= 2:
                water_count += 1
            else:
                water_count+=temp/2

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

# Earn 5 points for each mountain space connected to a farm space by a cluster of waters spaces
# This one is hard to make a greedy evaluation. Feel free to fork and improve.
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
        else:
            mountain_count += len(mountains)/2

    return mountain_count*5

# Earn 4 points for each column that contains an equal number of farm spaces and water spaces.
# There must be at least one of each.
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

# Earn 7 points for each cluster of farm spaces adjacent to three or more water spaces
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
        temp = count_adjacent_water(grid, cluster)
        if temp >= 3:
            count += 1
        else:
            count += temp/3

    return count*7

# Earn 7 points for each complete row or complete column of filled spaces that contains a mountain space
def dwarvenholds(grid):
    def contains_mountain(row):
        return "mountain" in row

    rows_count = 0
    cols_count = 0

    for row in grid:
        if contains_mountain(row):
            for cell in row:
                if cell!=0:
                    rows_count += 1/11

    for col in range(len(grid[0])):
        column = [grid[row][col] for row in range(len(grid))]
        if contains_mountain(column):
            for cell in column:
                if cell != 0:
                    cols_count += 1/11

    return 7*(rows_count + cols_count)

# Earn 4 points for each row that contains five or more different terrain types.
def bandedhills(grid):
    terrain_types = {"Forest", "Village", "Farm", "Water", "Monster", "Mountain"}
    row_count = 0

    for row in grid:
        unique_terrains = set(row)
        valid_terrains = unique_terrains.intersection(terrain_types)
        if len(valid_terrains) >= 5:
            row_count += 1
        else:
            row_count+=len(valid_terrains)/5

    return row_count*4

# Earn 4 points for each cluster of exactly three empty spaces surrounded on all sides by filled spaces
# or the edge of the map.
# TODO: I genuinely am blanking on how to implement this currently
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

# Earn 10 points for each complete odd-numbered column of filled spaces.
def silos(grid):
    def is_filled(column):
        return all(cell != 0 for cell in column)

    filled_odd_column_count = 0

    for col in range(0, len(grid[0]), 2):
        column = [grid[row][col] for row in range(len(grid))]
        for cell in column:
            if cell != 0:
                filled_odd_column_count += 1/11

    return filled_odd_column_count*10
