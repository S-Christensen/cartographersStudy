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

# Earn 2 points for each Forest space in the longest unbroken column of Forest spaces
def faunlostthicket(grid):
    if not grid or not grid[0]:
        return 0

    max_length = 0
    cols = len(grid[0])

    for col in range(cols):
        current_length = 0
        for row in grid:
            if row[col] == "Forest":
                current_length += 1
                max_length = max(max_length, current_length)
            else:
                current_length = 0

    return max_length*2

def is_surrounded_by_Forest_or_edge(grid, r, c):
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
            if grid[nr][nc] != "Forest":
                return False
        else:  # Out of bounds, considered as edge of the map
            continue
    return True

# Earn 2 points for each Forest space surrounded on all four sides by Forest spaces or the edge of the map
def heartoftheForest(grid):
    count = 0
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == "Forest":
                if is_surrounded_by_Forest_or_edge(grid, r, c):
                    count += 1
    return count*2

# Earn 4 points for each row that contains three or more Forest spaces
def sleepyvalley(grid):
    def count_Forests_in_row(row):
        return row.count("Forest")

    row_count = 0

    for row in grid:
        if count_Forests_in_row(row) >= 3:
            row_count += 1

    return row_count*4

def is_adjacent_to_Village(grid, cluster):
    for r, c in cluster:
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == "Village":
                return True
    return False

# Earn 6 points for each cluster of five or more Forest spaces not adjacent to any Village spaces
def deepwood(grid):
    visited = set()
    clusters = []

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if (row, col) not in visited and grid[row][col] == "Forest":
                cluster = dfs(grid, row, col, visited, "Forest")
                clusters.append(cluster)

    count = 0
    for cluster in clusters:
        if len(cluster) >= 5 and not is_adjacent_to_Village(grid, cluster):
            count += 1

    return count*6

# Earn 6 points for each cluster of Village spaces that contains four spaces in a 2x2 square
def gnomishcolony(grid, terrain_type="Village"):
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

# Earn 7 points for each cluster of Village spaces that contain 4 spaces in a 4x1 or 1x4 rectangle
def traylomonastery(grid):
    visited = set()
    clusters = []

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if (row, col) not in visited and grid[row][col] == "Village":
                cluster = dfs(grid, row, col, visited, "Village")
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

# Find the cluster of Village spaces that will give you the most points where you get 1 point for each row and column
# that contains a space from that cluster
def caravansary(grid):
    visited = set()
    clusters = []

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if (row, col) not in visited and grid[row][col] == "Village":
                cluster = dfs(grid, row, col, visited, "Village")
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
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and (grid[nr][nc] == "0" or grid[nr][nc] == "Ruins"):
                points += 1
    return points

# C# Find the cluster of Village spaces that will give you the most points where you get 1 point for each empty space
# adjacent to that cluster
def outerenclave(grid):
    visited = set()
    clusters = []

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if (row, col) not in visited and grid[row][col] == "Village":
                cluster = dfs(grid, row, col, visited, "Village")
                clusters.append(cluster)

    max_points = 0

    for cluster in clusters:
        points = calculate_points_for_empty_adjacent(grid, cluster)
        if points > max_points:
            max_points = points

    return max_points

# Earn 4 points for each Water space adjacent to two or more Farm spaces
def ulemswallow(grid):
    def is_Farm(r, c):
        return 0 <= r < len(grid) and 0 <= c < len(grid[0]) and grid[r][c] == "Farm"

    def count_adjacent_Farms(r, c):
        Farm_count = 0
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if is_Farm(nr, nc):
                Farm_count += 1
        return Farm_count

    Water_count = 0

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == "Water" and count_adjacent_Farms(r, c) >= 2:
                Water_count += 1

    return Water_count*4

def has_Mountain_and_Farm(grid, cluster):
    Mountains = set()
    Farms = set()

    for r, c in cluster:
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                if grid[nr][nc] == "Mountain":
                    Mountains.add((nr, nc))
                if grid[nr][nc] == "Farm":
                    Farms.add((nr, nc))
    return Mountains, Farms

# Earn 5 points for each Mountain space connected to a Farm space by a cluster of Waters paces
def clawsgravepeaks(grid):
    visited = set()
    clusters = []
    Mountain_count = 0

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if (row, col) not in visited and grid[row][col] == "Water":
                cluster = dfs(grid, row, col, visited, "Water")
                clusters.append(cluster)

    for cluster in clusters:
        Mountains, Farms = has_Mountain_and_Farm(grid, cluster)
        if Farms:
            Mountain_count += len(Mountains)

    return Mountain_count*5

# Earn 4 points for each column that contains an equal number of Farm spaces and Water spaces.
# There must be at least one of each.
def jorekburg(grid):
    column_count = 0

    for col in range(len(grid[0])):
        Farm_count = 0
        Water_count = 0
        for row in range(len(grid)):
            if grid[row][col] == "Farm":
                Farm_count += 1
            elif grid[row][col] == "Water":
                Water_count += 1
        if Farm_count == Water_count and Farm_count > 0:
            column_count += 1

    return column_count*4

def count_adjacent_Water(grid, cluster):
    Water_count = 0
    for r, c in cluster:
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == "Water":
                Water_count += 1
    return Water_count

# Earn 7 points for each cluster of Farm spaces adjacent to three or more Water spaces
def craylund(grid):
    visited = set()
    clusters = []

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if (row, col) not in visited and grid[row][col] == "Farm":
                cluster = dfs(grid, row, col, visited, "Farm")
                clusters.append(cluster)

    count = 0
    for cluster in clusters:
        if count_adjacent_Water(grid, cluster) >= 3:
            count += 1

    return count*7

# Earn 7 points for each complete row or complete column of filled spaces that contains a Mountain space
def dwarvenholds(grid):
    def is_filled(row):
        return all((cell != "0" or cell != "ruins") for cell in row)

    def contains_Mountain(row):
        return "Mountain" in row

    rows_count = 0
    cols_count = 0

    for row in grid:
        if is_filled(row) and contains_Mountain(row):
            rows_count += 1

    for col in range(len(grid[0])):
        column = [grid[row][col] for row in range(len(grid))]
        if is_filled(column) and contains_Mountain(column):
            cols_count += 1

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

    return row_count*4

# Earn 4 points for each cluster of exactly three empty spaces surrounded on all sides by filled spaces
# or the edge of the map.
def starlitsigil(grid):
    visited = set()
    clusters = []

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if (row, col) not in visited and (grid[row][col] == "0" or grid[row][col] == "Ruins"):
                cluster = dfs(grid, row, col, visited, 0)
                if len(cluster) == 3:
                    clusters.append(cluster)

    return len(clusters)*4

# Earn 10 points for each complete odd-numbered column of filled spaces.
def silos(grid):
    def is_filled(column):
        return all((cell != "0" or cell != "ruins") for cell in column)

    filled_odd_column_count = 0

    for col in range(0, len(grid[0]), 2):
        column = [grid[row][col] for row in range(len(grid))]
        if is_filled(column):
            filled_odd_column_count += 1

    return filled_odd_column_count*10

### BASE GAME SCORING
#Earn one point per row and column with at least one Forest space. The same Forest space can be scored in both a row and column
def greenbough(grid):
    total = 0
    colSet = set()
    for row in range(len(grid)):
        rowFlag = False
        for col in range(len(grid[0])):
            if grid[row][col] == "Forest":  # FIXED
                rowFlag = True
                colSet.add(col)
        if rowFlag:
            total += 1
    total += len(colSet)
    return total

# Earn 3 points for each Mountain space connected to another Mountain space by a cluster of Forest spaces
def stonesideForest(grid):
    visited = set()
    clusters = []

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if (r, c) not in visited and grid[r][c] == "Forest":
                cluster = dfs(grid, r, c, visited, "Forest")
                clusters.append(cluster)

    allmount = set()
    for cluster in clusters:
        Mountains = set()
        for r, c in cluster:
            for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == "Mountain":
                    Mountains.add((nr, nc))
        if len(Mountains) >= 2:
            allmount = allmount.union(Mountains)

    return len(allmount) * 3

# Earn one point for each Forest space adjacent to the edge of the map
def sentinelWood(grid):
    count = 0
    rows, cols = len(grid), len(grid[0])

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "Forest":
                if r == 0 or r == rows - 1 or c == 0 or c == cols - 1:
                    count += 1

    return count

# Earn one point for each Forest space surrounded on all four sides by filled spaces or the edge of the map
def treetower(grid):
    count = 0
    rows, cols = len(grid), len(grid[0])

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "Forest":
                surrounded = True
                for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and (grid[nr][nc] == "0" or grid[nr][nc] == "Ruins"):
                        surrounded = False
                        break
                if surrounded:
                    count += 1

    return count

# Earn one point for each Water space adjacent to a ruins space. Earn 3 points for each Farm space on a ruins space.
def goldenGranary(grid):
    points = 0
    ruins = [(1,5), (2,1), (2,8), (8,1), (8,9), (9,5)]

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == "Water":
                for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and (nr, nc) in ruins:
                        points += 1
                        break
            elif grid[r][c] == "Farm" and (r, c) in ruins:
                points += 3
    return points

# Earn 3 points for each cluster of Farm spaces not adjacent to a Water space or the edge of the map.
# Earn 3 points for each cluster of Water spaces not adjacent to a Farm space or the edge of the map.
def shoresideExpanse(grid):
    visited = set()
    Farm_clusters = []
    Water_clusters = []

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if (r, c) not in visited:
                if grid[r][c] == "Farm":
                    cluster = dfs(grid, r, c, visited, "Farm")
                    Farm_clusters.append(cluster)
                elif grid[r][c] == "Water":
                    cluster = dfs(grid, r, c, visited, "Water")
                    Water_clusters.append(cluster)

    def is_isolated(cluster, target):
        for r, c in cluster:
            for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < len(grid) and 0 <= nc < len(grid[0])):
                    return False
                if grid[nr][nc] == target:
                    return False
        return True

    count = 0
    for cluster in Farm_clusters:
        if is_isolated(cluster, "Water"):
            count += 1
    for cluster in Water_clusters:
        if is_isolated(cluster, "Farm"):
            count += 1

    return count * 3

# Earn one point for each Water space adjacent to at least one Farm space. Earn one point for each Farm space adjacent to at least one Water space.
def canalLake(grid):
    points = 0
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] in ["Water", "Farm"]:
                target = "Farm" if grid[r][c] == "Water" else "Water"
                for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == target:
                        points += 1
                        break
    return points

# Earn 2 points for each Water space adjacent to a Mountain space. Earn one point for each Farm space adjacent to a Mountain space.
def magesValley(grid):
    points = 0
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] in ["Water", "Farm"]:
                value = 2 if grid[r][c] == "Water" else 1
                for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == "Mountain":
                        points += value
                        break
    return points

# Earn 3 points for each cluster of Village spaces adjacent to three or more different terrain types
def greengoldPlains(grid):
    visited = set()
    clusters = []

    terrain_types = {"Forest", "Farm", "Water", "Monster", "Mountain"}

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if (r, c) not in visited and grid[r][c] == "Village":
                cluster = dfs(grid, r, c, visited, "Village")
                clusters.append(cluster)

    count = 0
    for cluster in clusters:
        adjacent_types = set()
        for r, c in cluster:
            for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                    t = grid[nr][nc]
                    if t in terrain_types:
                        adjacent_types.add(t)
        if len(adjacent_types) >= 3:
            count += 1

    return count * 3

# Earn 2 points for each Village space in the 2nd largest cluster of Village spaces
def shieldgate(grid):
    visited = set()
    clusters = []

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if (r, c) not in visited and grid[r][c] == "Village":
                cluster = dfs(grid, r, c, visited, "Village")
                clusters.append(cluster)

    clusters.sort(key=len, reverse=True)
    if len(clusters) >= 2:
        return len(clusters[1]) * 2
    return 0

# Earn one point for each Village space in the largest cluster of Village spaces that is not adjacent to a Mountain space
def greatCity(grid):
    visited = set()
    valid_clusters = []

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if (r, c) not in visited and grid[r][c] == "Village":
                cluster = dfs(grid, r, c, visited, "Village")

                # Check if any tile in cluster is adjacent to a Mountain
                adjacent_to_Mountain = False
                for x, y in cluster:
                    for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                            if grid[nx][ny] == "Mountain":
                                adjacent_to_Mountain = True
                                break
                    if adjacent_to_Mountain:
                        break

                if not adjacent_to_Mountain:
                    valid_clusters.append(cluster)

    if not valid_clusters:
        return 0

    largest = max(valid_clusters, key=len)
    return len(largest)

# Earn 8 points for each cluster of 6 or more Village spaces
def wildholds(grid):
    visited = set()
    count = 0

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if (r, c) not in visited and grid[r][c] == "Village":
                cluster = dfs(grid, r, c, visited, "Village")
                if len(cluster) >= 6:
                    count += 1

    return count * 8

# Earn 6 points for each complete row or complete column of filled spaces
def borderlands(grid):
    def is_filled(line):
        return all((cell != "0" or cell != "ruins") for cell in line)

    row_count = sum(1 for row in grid if is_filled(row))

    col_count = 0
    for c in range(len(grid[0])):
        column = [grid[r][c] for r in range(len(grid))]
        if is_filled(column):
            col_count += 1

    return (row_count + col_count) * 6

# Earn 3 points for each complete diagonal line of filled spaces that touches the left and bottom edges of the map
def brokenRoad(grid):
    rows, cols = len(grid), len(grid[0])
    count = 0

    for start in range(rows):
        r, c = start, 0
        diagonal = []
        while r >= 0 and c < cols:
            diagonal.append(grid[r][c])
            r -= 1
            c += 1
        if all((cell != "0" or cell != "ruins") for cell in diagonal):
            count += 1

    return count * 3

# Earn one point for each empty space surrounded on all four sides by filled spaces or the edge of the map
def cauldrons(grid):
    count = 0
    rows, cols = len(grid), len(grid[0])

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "0" or grid[r][c] == "Ruins":
                surrounded = True
                for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and (grid[nr][nc] == "0" or grid[nr][nc] == "Ruins"):
                        surrounded = False
                        break
                if surrounded:
                    count += 1

    return count

# Earn 3 points for each space along one edge of the largest square of filled spaces
def lostBarony(grid):
    rows, cols = len(grid), len(grid[0])
    max_size = 0

    for r in range(rows):
        for c in range(cols):
            for size in range(1, min(rows - r, cols - c) + 1):
                filled = True
                for i in range(size):
                    for j in range(size):
                        if grid[r + i][c + j] == "0" or grid[r + i][c + j] == "Ruins":
                            filled = False
                            break
                    if not filled:
                        break
                if filled and size > max_size:
                    max_size = size

    return max_size * 3