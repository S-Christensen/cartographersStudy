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
'''
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
    outcome = 0
    for nr, nc in surroundings:
        if 0 <= nr < rows and 0 <= nc < cols:
            if grid[nr][nc] == "Forest":
                outcome+=1
        else:  # Out of bounds, considered as edge of the map
            outcome += 1
            continue
    return outcome

# Earn 2 points for each Forest space surrounded on all four sides by Forest spaces or the edge of the map
def heartoftheForest(grid):
    count = 0.0
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == "Forest":
                count += is_surrounded_by_Forest_or_edge(grid, r, c)/4
    return count*2

# Earn 4 points for each row that contains three or more Forest spaces
def sleepyvalley(grid, current_rows):
    row_count = 0
    straggler = 0

    for row in grid:
        if row.count("Forest") >= 3:
            row_count += 1
        else:
            row_count += (row.count("Forest")/3)

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
        elif not is_adjacent_to_Village(grid, cluster):
            count+=len(cluster)/5

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
        else:
            champ = 0
            for r, c in set(cluster):
                # Check for 4x1 rectangle
                i=0
                while (r, c + i) in set(cluster) == "Village":
                    i+=1
                # Check for 1x4 rectangle
                j=0
                if (r + j, c) in set(cluster) == "Village":
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
            temp = count_adjacent_Farms(r, c)
            if grid[r][c] == "Water" and temp >= 2:
                Water_count += 1
            else:
                Water_count+=temp/2

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

# Earn 5 points for each Mountain space connected to a Farm space by a cluster of Waters spaces
# This one is hard to make a greedy evaluation. Feel free to fork and improve.
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
        else:
            Mountain_count += len(Mountains)/2

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
        temp = count_adjacent_Water(grid, cluster)
        if temp >= 3:
            count += 1
        else:
            count += temp/3

    return count*7

# Earn 7 points for each complete row or complete column of filled spaces that contains a Mountain space
def dwarvenholds(grid):
    def contains_Mountain(row):
        return "Mountain" in row

    rows_count = 0
    cols_count = 0

    for row in grid:
        if contains_Mountain(row):
            for cell in row:
                if cell!=0:
                    rows_count += 1/11

    for col in range(len(grid[0])):
        column = [grid[row][col] for row in range(len(grid))]
        if contains_Mountain(column):
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
'''

def penalize_surrounded_empty(prev_grid, action):
    rows, cols = len(prev_grid), len(prev_grid[0])
    penalty = 0.0

    for (r, c) in action["cells"]:
        # Check all neighbors of the placed tile
        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            er, ec = r + dr, c + dc

            # If neighbor was empty/ruins BEFORE placement
            if 0 <= er < rows and 0 <= ec < cols and prev_grid[er][ec] in ("0", "Ruins"):

                # Count how many neighbors of that empty tile are filled AFTER placement
                filled = 0
                for dr2, dc2 in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nr, nc = er + dr2, ec + dc2
                    if 0 <= nr < rows and 0 <= nc < cols:
                        # After placement, this tile is filled if:
                        # - it was filled before, OR
                        # - it is one of the newly placed cells
                        if prev_grid[nr][nc] != "0" and prev_grid[nr][nc] != "Ruins":
                            filled += 1
                        elif (nr, nc) in action["cells"]:
                            filled += 1

                if filled == 4:
                    penalty -= 0.25

    return penalty

### BASE GAME SCORING
#Earn one point per row and column with at least one Forest space. The same Forest space can be scored in both a row and column
def greenbough_progress(grid):
    rows, cols = len(grid), len(grid[0])
    row_count = 0
    col_set = set()

    for r in range(rows):
        row_has_forest = False
        for c in range(cols):
            if grid[r][c] == "Forest":
                row_has_forest = True
                col_set.add(c)
        if row_has_forest:
            row_count += 1

    return row_count + len(col_set)

'''
Shaping logic
• 	+0.2 for placing a Forest in a row/column that previously had none
'''
def greenbough_reward(prev_grid, curr_grid, action):
    prev = greenbough_progress(prev_grid)
    curr = greenbough_progress(curr_grid)
    reward = curr - prev

    rows, cols = len(prev_grid), len(prev_grid[0])

    for (r, c) in action["cells"]:
        row_prev = any(prev_grid[r][x] == "Forest" for x in range(cols))
        col_prev = any(prev_grid[x][c] == "Forest" for x in range(rows))

        if action["terrain"] == "Forest":
            if not row_prev:
                reward += 0.2
            if not col_prev:
                reward += 0.2

    return reward

# Earn 3 points for each Mountain space connected to another Mountain space by a cluster of Forest spaces
def stoneside_progress(grid):
    visited = set()
    clusters = []

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if (r, c) not in visited and grid[r][c] == "Forest":
                cluster = dfs(grid, r, c, visited, "Forest")
                clusters.append(cluster)

    connected_mountains = set()

    for cluster in clusters:
        mountains = set()
        for r, c in cluster:
            for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                    if grid[nr][nc] == "Mountain":
                        mountains.add((nr, nc))

        if len(mountains) >= 2:
            connected_mountains |= mountains

    return len(connected_mountains) * 3

'''
Shaping logic
• 	+0.2 for placing a Forest in a row/column that previously had none
• 	−0.1 for placing a non‑Forest in an empty row/column (blocks potential)
'''
def stoneside_reward(prev_grid, curr_grid, action):
    prev = stoneside_progress(prev_grid)
    curr = stoneside_progress(curr_grid)
    reward = curr - prev

    rows, cols = len(prev_grid), len(prev_grid[0])

    # Check adjacency to mountains
    for (r, c) in action["cells"]:
        adjacent_mountain = False
        adjacent_forest_prev = 0

        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if prev_grid[nr][nc] == "Mountain":
                    adjacent_mountain = True
                if prev_grid[nr][nc] == "Forest":
                    adjacent_forest_prev += 1

        if action["terrain"] == "Forest":
            if adjacent_mountain:
                reward += 0.3
            if adjacent_forest_prev >= 2:
                reward += 0.4  # likely connecting clusters
        else:
            if adjacent_mountain:
                reward -= 0.1

    return reward

# Earn one point for each Forest space adjacent to the edge of the map
def sentinel_progress(grid):
    rows, cols = len(grid), len(grid[0])
    count = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "Forest":
                if r == 0 or r == rows - 1 or c == 0 or c == cols - 1:
                    count += 1

    return count

'''
Shaping logic
• -0.2 for non-Forest placed on the edge
• -0.1 for non-Forest placed near the edge (distance 1)
'''
def sentinel_reward(prev_grid, curr_grid, action):
    prev = sentinel_progress(prev_grid)
    curr = sentinel_progress(curr_grid)
    reward = curr - prev

    rows, cols = len(prev_grid), len(prev_grid[0])

    for (r, c) in action["cells"]:
        is_edge = (r == 0 or r == rows - 1 or c == 0 or c == cols - 1)
        is_near_edge = (r == 1 or r == rows - 2 or c == 1 or c == cols - 2)

        # Only shaping needed: penalize non-Forest on or near the edge
        if action["terrain"] != "Forest":
            if is_edge:
                reward -= 0.2
            elif is_near_edge:
                reward -= 0.1

    return reward



# Earn one point for each Forest space surrounded on all four sides by filled spaces or the edge of the map
def treetower_progress(grid):
    rows, cols = len(grid), len(grid[0])
    count = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "Forest":
                surrounded = True
                for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if grid[nr][nc] in ("0", "Ruins"):
                            surrounded = False
                            break
                if surrounded:
                    count += 1

    return count


def treetower_reward(prev_grid, curr_grid, action):
    prev = treetower_progress(prev_grid)
    curr = treetower_progress(curr_grid)
    reward = curr - prev

    rows, cols = len(prev_grid), len(prev_grid[0])

    for (r, c) in action["cells"]:

        # Reward placing a Forest inversely proportional to empty neighbors
        if action["terrain"] == "Forest":
            empty_neighbors = 0
            for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    if prev_grid[nr][nc] in ("0", "Ruins"):
                        empty_neighbors += 1

            # Inverse reward: fewer empty neighbors = higher reward
            reward += (4 - empty_neighbors) * 0.1 

        # Reward helping existing Forests become surrounded
        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            fr, fc = r + dr, c + dc
            if 0 <= fr < rows and 0 <= fc < cols and prev_grid[fr][fc] == "Forest":

                empty_neighbors_before = 0
                for dr2, dc2 in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nr, nc = fr + dr2, fc + dc2
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if prev_grid[nr][nc] in ("0", "Ruins"):
                            empty_neighbors_before += 1

                if action["terrain"] == "Forest":
                    if empty_neighbors_before == 1:
                        reward += 0.3
                    elif empty_neighbors_before == 2:
                        reward += 0.15
                else:
                    if empty_neighbors_before <= 2:
                        reward -= 0.2

    # Penalize creating a trapped empty tile next to a Forest
    for (r, c) in action["cells"]:
        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            er, ec = r + dr, c + dc

            # Check if this neighbor was empty BEFORE placement
            if 0 <= er < rows and 0 <= ec < cols and prev_grid[er][ec] in ("0", "Ruins"):

                # Count filled neighbors AFTER placement
                filled = 0
                for dr2, dc2 in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nr, nc = er + dr2, ec + dc2
                    if 0 <= nr < rows and 0 <= nc < cols:
                        # Filled if it was filled before OR is newly placed
                        if prev_grid[nr][nc] not in ("0", "Ruins") or (nr, nc) in action["cells"]:
                            filled += 1

                # If the empty tile is now fully surrounded
                if filled == 4:
                    # Check if that empty tile is next to a Forest
                    next_to_forest = False
                    for dr3, dc3 in [(1,0), (-1,0), (0,1), (0,-1)]:
                        fr, fc = er + dr3, ec + dc3
                        if 0 <= fr < rows and 0 <= fc < cols:
                            if prev_grid[fr][fc] == "Forest":
                                next_to_forest = True
                                break

                    if next_to_forest:
                        reward -= 0.25
    return reward


# Earn one point for each Water space adjacent to a ruins space. Earn 3 points for each Farm space on a ruins space.
def goldenGranary_progress(grid):
    points = 0
    ruins = {(1,5), (2,1), (2,8), (8,1), (8,9), (9,5)}

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == "Water":
                for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nr, nc = r + dr, c + dc
                    if (nr, nc) in ruins:
                        points += 1
                        break
            elif grid[r][c] == "Farm" and (r, c) in ruins:
                points += 3

    return points

'''
Shaping logic
• 	+0.3 for placing Water adjacent to a ruins tile
• 	+0.5 for placing Farm on a ruins tile
• 	−0.1 for placing non‑Water next to ruins (blocks adjacency potential)
• 	−0.2 for placing non‑Farm on a ruins tile
'''
def goldenGranary_reward(prev_grid, curr_grid, action):
    prev = goldenGranary_progress(prev_grid)
    curr = goldenGranary_progress(curr_grid)
    reward = curr - prev

    ruins = {(1,5), (2,1), (2,8), (8,1), (8,9), (9,5)}
    rows, cols = len(prev_grid), len(prev_grid[0])

    for (r, c) in action["cells"]:
        # Farm on ruins
        if (r, c) in ruins:
            if action["terrain"] == "Farm":
                reward += 0.5
            else:
                reward -= 0.2

        # Water adjacent to ruins
        adjacent_ruins = False
        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            nr, nc = r + dr, c + dc
            if (nr, nc) in ruins:
                adjacent_ruins = True

        if adjacent_ruins:
            if action["terrain"] == "Water":
                reward += 0.3
            else:
                reward -= 0.1

    return reward

# Earn 3 points for each cluster of Farm spaces not adjacent to a Water space or the edge of the map.
# Earn 3 points for each cluster of Water spaces not adjacent to a Farm space or the edge of the map.
def shoreside_progress(grid):
    visited = set()
    farm_clusters = []
    water_clusters = []

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if (r, c) not in visited:
                if grid[r][c] == "Farm":
                    cluster = dfs(grid, r, c, visited, "Farm")
                    farm_clusters.append(cluster)
                elif grid[r][c] == "Water":
                    cluster = dfs(grid, r, c, visited, "Water")
                    water_clusters.append(cluster)

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
    for cluster in farm_clusters:
        if is_isolated(cluster, "Water"):
            count += 1
    for cluster in water_clusters:
        if is_isolated(cluster, "Farm"):
            count += 1

    return count * 3

def shoreside_reward(prev_grid, curr_grid, action):
    return shoreside_progress(curr_grid) - shoreside_progress(prev_grid)

# Earn one point for each Water space adjacent to at least one Farm space. Earn one point for each Farm space adjacent to at least one Water space.
def canalLake_progress(grid):
    points = 0
    rows, cols = len(grid), len(grid[0])

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] in ("Water", "Farm"):
                target = "Farm" if grid[r][c] == "Water" else "Water"
                for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == target:
                        points += 1
                        break

    return points

def canalLake_reward(prev_grid, curr_grid, action):
    prev = canalLake_progress(prev_grid)
    curr = canalLake_progress(curr_grid)
    reward = curr - prev

    rows, cols = len(prev_grid), len(prev_grid[0])
    terrain = action["terrain"]

    for (r, c) in action["cells"]:
        is_edge = (r == 0 or r == rows - 1 or c == 0 or c == cols - 1)

        # 1. Penalize placing Water/Farm on the edge
        if terrain in ("Water", "Farm") and is_edge:
            reward -= 0.1

        # 2. Penalize placing Water next to Water, Farm next to Farm
        same_type_neighbors = 0
        opposite_type_neighbors = 0
        blocking_neighbors = 0

        opposite = "Farm" if terrain == "Water" else "Water"

        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                neighbor = prev_grid[nr][nc]

                if terrain in ("Water", "Farm"):
                    if neighbor == terrain:
                        same_type_neighbors += 1
                    elif neighbor == opposite:
                        opposite_type_neighbors += 1
                    elif neighbor not in ("0", "Ruins"):
                        blocking_neighbors += 1

                else:
                    # Non-water/farm placed next to water/farm
                    if neighbor in ("Water", "Farm"):
                        blocking_neighbors += 1

        # Penalize same-type adjacency (blocks scoring potential)
        if terrain in ("Water", "Farm"):
            reward -= 0.1 * same_type_neighbors

        # Penalize blocking neighbors (irrelevant terrain next to W/F)
        reward -= 0.1 * blocking_neighbors

    return reward


# Earn 2 points for each Water space adjacent to a Mountain space. Earn one point for each Farm space adjacent to a Mountain space.
def magesValley_progress(grid):
    points = 0
    rows, cols = len(grid), len(grid[0])

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] in ("Water", "Farm"):
                value = 2 if grid[r][c] == "Water" else 1
                for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "Mountain":
                        points += value
                        break

    return points

'''
Shaping logic
- −0.1 for placing non‑Water/Farm next to Mountain (blocks scoring potential)
'''
def magesValley_reward(prev_grid, curr_grid, action):
    prev = magesValley_progress(prev_grid)
    curr = magesValley_progress(curr_grid)
    reward = curr - prev

    rows, cols = len(prev_grid), len(prev_grid[0])
    terrain = action["terrain"]

    for (r, c) in action["cells"]:
        adjacent_mountain = False

        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if prev_grid[nr][nc] == "Mountain":
                    adjacent_mountain = True

        if adjacent_mountain:
            if terrain != "Water" and terrain != "Farm":
                reward -= 0.1

    return reward

# Earn 3 points for each cluster of Village spaces adjacent to three or more different terrain types
def greengoldPlains_progress(grid):
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


def greengoldPlains_reward(prev_grid, curr_grid, action):
    prev = greengoldPlains_progress(prev_grid)
    curr = greengoldPlains_progress(curr_grid)
    reward = curr - prev

    rows, cols = len(prev_grid), len(prev_grid[0])
    terrain_types = {"Forest", "Farm", "Water", "Monster", "Mountain"}

    # Identify Village clusters in the previous grid
    visited = set()
    prev_clusters = []

    for r in range(rows):
        for c in range(cols):
            if (r, c) not in visited and prev_grid[r][c] == "Village":
                cluster = dfs(prev_grid, r, c, visited, "Village")
                prev_clusters.append(cluster)

    # Precompute adjacency types for each cluster
    cluster_adj_types = []
    for cluster in prev_clusters:
        adj = set()
        for r, c in cluster:
            for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    t = prev_grid[nr][nc]
                    if t in terrain_types:
                        adj.add(t)
        cluster_adj_types.append(adj)

    for (r, c) in action["cells"]:
        if action["terrain"] != "Village":
            continue

        # Penalize placing Village near the edge
        if r == 0 or r == rows - 1 or c == 0 or c == cols - 1:
            reward -= 0.2
        elif r == 1 or r == rows - 2 or c == 1 or c == cols - 2:
            reward -= 0.1

        # Penalize placing Village next to Village
        village_neighbors = 0
        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if prev_grid[nr][nc] == "Village":
                    village_neighbors += 1

        reward -= 0.1 * village_neighbors

        # Determine whether this touches an existing cluster
        touches_cluster = False
        touched_cluster_index = None

        for i, cluster in enumerate(prev_clusters):
            if any(abs(r - x) + abs(c - y) == 1 for (x, y) in cluster):
                touches_cluster = True
                touched_cluster_index = i
                break

        # Reward creating a new cluster
        if not touches_cluster:
            reward += 0.3

            # Reward adjacency to non-village terrain types
            new_adj_types = set()
            for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    t = prev_grid[nr][nc]
                    if t in terrain_types:
                        new_adj_types.add(t)

            reward += 0.1 * len(new_adj_types)
            continue

        # Reward adding new adjacency types to an existing cluster
        prev_adj = cluster_adj_types[touched_cluster_index]

        new_types = set()
        repeated_types = 0

        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                t = prev_grid[nr][nc]
                if t in terrain_types:
                    if t not in prev_adj:
                        new_types.add(t)
                    else:
                        repeated_types += 1

        reward += 0.15 * len(new_types)
        reward -= 0.05 * repeated_types

    return reward

# Earn 2 points for each Village space in the 2nd largest cluster of Village spaces
def shieldgate_progress(grid):
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


def shieldgate_reward(prev_grid, curr_grid, action):
    prev = shieldgate_progress(prev_grid)
    curr = shieldgate_progress(curr_grid)
    reward = curr - prev

    rows, cols = len(prev_grid), len(prev_grid[0])

    # penalize placing non-Village next to Village
    for (r, c) in action["cells"]:
        if action["terrain"] == "Village":
            continue

        # Check if this non-Village tile touches any Village
        touches_village = False
        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if prev_grid[nr][nc] == "Village":
                    touches_village = True
                    break

        if touches_village:
            reward -= 0.2

    return reward

# Earn one point for each Village space in the largest cluster of Village spaces that is not adjacent to a Mountain space
def greatCity_progress(grid):
    visited = set()
    valid_clusters = []

    rows, cols = len(grid), len(grid[0])

    for r in range(rows):
        for c in range(cols):
            if (r, c) not in visited and grid[r][c] == "Village":
                cluster = dfs(grid, r, c, visited, "Village")

                adjacent_to_mountain = False
                for x, y in cluster:
                    for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < rows and 0 <= ny < cols:
                            if grid[nx][ny] == "Mountain":
                                adjacent_to_mountain = True
                                break
                    if adjacent_to_mountain:
                        break

                if not adjacent_to_mountain:
                    valid_clusters.append(cluster)

    if not valid_clusters:
        return 0

    largest = max(valid_clusters, key=len)
    return len(largest)

def greatCity_reward(prev_grid, curr_grid, action):
    prev = greatCity_progress(prev_grid)
    curr = greatCity_progress(curr_grid)
    reward = curr - prev

    rows, cols = len(prev_grid), len(prev_grid[0])

    # penalize placing non-Village next to Village
    for (r, c) in action["cells"]:
        if action["terrain"] == "Village":
            continue

        touches_village = False
        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if prev_grid[nr][nc] == "Village":
                    touches_village = True
                    break

        if touches_village:
            reward -= 0.2

    return reward

# Earn 8 points for each cluster of 6 or more Village spaces
def wildholds_progress(grid):
    visited = set()
    count = 0

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if (r, c) not in visited and grid[r][c] == "Village":
                cluster = dfs(grid, r, c, visited, "Village")
                if len(cluster) >= 6:
                    count += 1

    return count * 8


def wildholds_reward(prev_grid, curr_grid, action):
    prev = wildholds_progress(prev_grid)
    curr = wildholds_progress(curr_grid)
    reward = curr - prev

    rows, cols = len(prev_grid), len(prev_grid[0])

    # Identify Village clusters in the previous grid
    visited = set()
    prev_clusters = []

    for r in range(rows):
        for c in range(cols):
            if (r, c) not in visited and prev_grid[r][c] == "Village":
                cluster = dfs(prev_grid, r, c, visited, "Village")
                prev_clusters.append(cluster)

    for (r, c) in action["cells"]:
        terrain = action["terrain"]

        if terrain == "Village":
            # Check adjacency to existing clusters
            touched_clusters = []

            for cluster in prev_clusters:
                if any(abs(r - x) + abs(c - y) == 1 for (x, y) in cluster):
                    touched_clusters.append(cluster)

            # If it touches no cluster → new cluster → neutral
            if not touched_clusters:
                continue

            # If it touches one or more clusters, evaluate each
            for cluster in touched_clusters:
                size = len(cluster)

                if 1 <= size <= 5:
                    # Reward growing clusters that can still reach size 6
                    reward += 0.2
                elif size >= 6:
                    # Penalize growing clusters that are already "complete"
                    reward -= 0.2

            continue

        # Penalize placing NON-Village next to Village
        touches_village = False
        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if prev_grid[nr][nc] == "Village":
                    touches_village = True
                    break

        if touches_village:
            reward -= 0.2

    return reward


# Earn 6 points for each complete row or complete column of filled spaces
def borderlands_progress(grid):
    def is_filled(line):
        return all(cell not in ("0", "Ruins") for cell in line)

    rows = len(grid)
    cols = len(grid[0])

    row_count = sum(1 for r in range(rows) if is_filled(grid[r]))
    col_count = sum(1 for c in range(cols) if is_filled([grid[r][c] for r in range(rows)]))

    return (row_count + col_count) * 6

'''
Shaping logic
- +0.3 for placing terrain in a row/column that is almost full (missing 1–2 cells)
- +0.2 for placing terrain in any partially filled row/column
- −0.1 for placing terrain in a row/column with no filled neighbors (isolated)
'''
def borderlands_reward(prev_grid, curr_grid, action):
    prev = borderlands_progress(prev_grid)
    curr = borderlands_progress(curr_grid)
    reward = curr - prev

    rows, cols = len(prev_grid), len(prev_grid[0])

    for (r, c) in action["cells"]:
        # Count filled cells in row/column BEFORE placement
        row_filled = sum(prev_grid[r][x] not in ("0", "Ruins") for x in range(cols))
        col_filled = sum(prev_grid[x][c] not in ("0", "Ruins") for x in range(rows))

        # Row shaping
        if row_filled == cols - 1:
            reward += 0.3
        elif row_filled >= cols - 3:
            reward += 0.2
        elif row_filled == 0:
            reward -= 0.1

        # Column shaping
        if col_filled == rows - 1:
            reward += 0.3
        elif col_filled >= rows - 3:
            reward += 0.2
        elif col_filled == 0:
            reward -= 0.1
    reward += penalize_surrounded_empty(prev_grid, action)
    return reward

# Earn 3 points for each complete diagonal line of filled spaces that touches the left and bottom edges of the map
def brokenRoad_progress(grid):
    rows, cols = len(grid), len(grid[0])
    count = 0

    for start in range(rows):
        r, c = start, 0
        diagonal = []
        while r >= 0 and c < cols:
            diagonal.append(grid[r][c])
            r -= 1
            c += 1

        if all(cell not in ("0", "Ruins") for cell in diagonal):
            count += 1

    return count * 3

'''
Shaping logic
- +0.3 for placing terrain on a diagonal that is nearly complete
- +0.2 for placing terrain on any diagonal
- −0.1 for placing terrain that isolates a diagonal cell
'''
def brokenRoad_reward(prev_grid, curr_grid, action):
    prev = brokenRoad_progress(prev_grid)
    curr = brokenRoad_progress(curr_grid)
    reward = curr - prev

    rows, cols = len(prev_grid), len(prev_grid[0])

    # Precompute diagonals
    diagonals = []
    for start in range(rows):
        diag = []
        r, c = start, 0
        while r >= 0 and c < cols:
            diag.append((r, c))
            r -= 1
            c += 1
        diagonals.append(diag)

    for (r, c) in action["cells"]:
        for diag in diagonals:
            if (r, c) in diag:
                # Count filled before placement
                filled_before = sum(prev_grid[x][y] not in ("0", "Ruins") for (x, y) in diag)
                if filled_before == len(diag) - 1:
                    reward += 0.3
                elif filled_before >= len(diag) - 3:
                    reward += 0.2
                elif filled_before == 0:
                    reward -= 0.1
    reward += penalize_surrounded_empty(prev_grid, action)
    return reward

# Earn one point for each empty space surrounded on all four sides by filled spaces or the edge of the map
def cauldrons_progress(grid):
    rows, cols = len(grid), len(grid[0])
    count = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] in ("0", "Ruins"):
                surrounded = True
                for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if grid[nr][nc] in ("0", "Ruins"):
                            surrounded = False
                            break
                if surrounded:
                    count += 1

    return count

def penalize_surrounded_empty_clusters(prev_grid, curr_grid, action):
    rows, cols = len(prev_grid), len(prev_grid[0])
    penalty = 0.0

    # Identify empty/ruins clusters in the CURRENT grid
    visited = set()
    clusters = []

    for r in range(rows):
        for c in range(cols):
            if (r, c) not in visited and curr_grid[r][c] in ("0", "Ruins"):
                cluster = dfs(curr_grid, r, c, visited, ("0", "Ruins"))
                clusters.append(cluster)

    # Check which clusters are fully surrounded
    for cluster in clusters:
        fully_surrounded = True

        for (r, c) in cluster:
            for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    if curr_grid[nr][nc] in ("0", "Ruins"):
                        continue
                else:
                    fully_surrounded = False
                    break

            if not fully_surrounded:
                break

        # Penalize clusters of size >= 2 that are fully surrounded
        if fully_surrounded and len(cluster) >= 2:
            penalty -= 0.3

    return penalty

'''
Shaping logic
- +0.3 for placing terrain that creates a new surrounded empty
- +0.2 for placing terrain that increases “surroundedness” of nearby empties
'''
def cauldrons_reward(prev_grid, curr_grid, action):
    prev = cauldrons_progress(prev_grid)
    curr = cauldrons_progress(curr_grid)
    reward = curr - prev

    rows, cols = len(prev_grid), len(prev_grid[0])

    for (r, c) in action["cells"]:
        # Check neighbors that were empty before
        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if prev_grid[nr][nc] in ("0", "Ruins"):
                    # Count filled neighbors before
                    filled_neighbors = 0
                    for dr2, dc2 in [(1,0), (-1,0), (0,1), (0,-1)]:
                        rr, cc = nr + dr2, nc + dc2
                        if 0 <= rr < rows and 0 <= cc < cols:
                            if prev_grid[rr][cc] not in ("0", "Ruins"):
                                filled_neighbors += 1

                    if action["terrain"] not in ("0", "Ruins"):
                        if filled_neighbors == 2:
                            reward += 0.2
                            
    reward += penalize_surrounded_empty_clusters(prev_grid, curr_grid, action)
    return reward

# Earn 3 points for each space along one edge of the largest square of filled spaces
def lostBarony_progress(grid):
    rows, cols = len(grid), len(grid[0])
    max_size = 0

    for r in range(rows):
        for c in range(cols):
            for size in range(1, min(rows - r, cols - c) + 1):
                filled = True
                for i in range(size):
                    for j in range(size):
                        if grid[r+i][c+j] in ("0", "Ruins"):
                            filled = False
                            break
                    if not filled:
                        break
                if filled and size > max_size:
                    max_size = size

    return max_size * 3


def lostBarony_reward(prev_grid, curr_grid, action):
    prev = lostBarony_progress(prev_grid)
    curr = lostBarony_progress(curr_grid)
    reward = curr - prev

    rows, cols = len(prev_grid), len(prev_grid[0])

    # Precompute potential squares in prev grid
    potential_squares = []
    for r in range(rows):
        for c in range(cols):
            for size in range(1, min(rows - r, cols - c) + 1):
                potential_squares.append((r, c, size))

    for (r, c) in action["cells"]:
        for (sr, sc, size) in potential_squares:
            if sr <= r < sr + size and sc <= c < sc + size:
                # Count filled cells before
                filled_before = 0
                total = size * size

                for i in range(size):
                    for j in range(size):
                        if prev_grid[sr+i][sc+j] not in ("0", "Ruins"):
                            filled_before += 1

                if action["terrain"] in ("0", "Ruins"):
                    reward -= 0.2
                else:
                    if filled_before == total - 1:
                        reward += 0.4
                    elif filled_before >= total - 3:
                        reward += 0.3
                    elif filled_before <= 1:
                        reward -= 0.1
    reward += penalize_surrounded_empty(prev_grid, action)

    return reward
