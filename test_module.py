import scoringCards
import unittest

def create_base_grid():
    grid = [[0 for _ in range(11)] for _ in range(11)]
    grid[1][3] = "mountain"
    grid[2][8] = "mountain"
    grid[5][5] = "mountain"
    grid[8][2] = "mountain"
    grid[9][7] = "mountain"
    return grid

class TestForestScoring(unittest.TestCase):

    def test_greenbough_empty(self):
        grid = create_base_grid()
        self.assertEqual(scoringCards.greenbough(grid), 0)

    def test_greenbough_rows_and_cols(self):
        grid = create_base_grid()
        grid[0][0] = "forest"
        grid[1][1] = "forest"
        grid[2][0] = "forest"
        grid[3][1] = "forest"
        # Rows: 0,1,2,3 → 4 points
        # Cols: 0,1 → 2 points
        self.assertEqual(scoringCards.greenbough(grid), 6)

    def test_stonesideForest_no_clusters(self):
        grid = create_base_grid()
        grid[0][0] = "forest"
        grid[10][10] = "forest"
        self.assertEqual(scoringCards.stonesideForest(grid), 0)

    def test_stonesideForest_connected_mountains(self):
        grid = create_base_grid()
        # Create forest cluster connecting (1,3) and (2,8)
        grid[1][4] = "forest"
        grid[1][5] = "forest"
        grid[2][5] = "forest"
        grid[2][6] = "forest"
        grid[2][7] = "forest"
        self.assertEqual(scoringCards.stonesideForest(grid), 6)  # 2 mountains × 3

    def test_sentinelWood_edges(self):
        grid = create_base_grid()
        grid[0][0] = "forest"
        grid[10][10] = "forest"
        grid[5][0] = "forest"
        grid[0][5] = "forest"
        grid[5][5] = "forest"  # not edge
        self.assertEqual(scoringCards.sentinelWood(grid), 4)

    def test_treetower_surrounded(self):
        grid = create_base_grid()
        grid[5][5] = "forest"
        grid[4][5] = "mountain"
        grid[6][5] = "mountain"
        grid[5][4] = "mountain"
        grid[5][6] = "mountain"
        self.assertEqual(scoringCards.treetower(grid), 1)

    def test_treetower_not_surrounded(self):
        grid = create_base_grid()
        grid[5][5] = "forest"
        grid[4][5] = 0
        grid[6][5] = "mountain"
        grid[5][4] = "mountain"
        grid[5][6] = "mountain"
        self.assertEqual(scoringCards.treetower(grid), 0)

class TestWaterFarmScoring(unittest.TestCase):

    def test_goldenGranary_water_adjacent_to_ruins(self):
        grid = create_base_grid()
        grid[1][4] = "water"  # adjacent to (1,5)
        grid[2][0] = "water"  # adjacent to (2,1)
        grid[2][7] = "water"  # adjacent to (2,8)
        grid[8][0] = "water"  # adjacent to (8,1)
        grid[8][8] = "water"  # adjacent to (8,9)
        grid[9][4] = "water"  # adjacent to (9,5)
        self.assertEqual(scoringCards.goldenGranary(grid), 6)

    def test_goldenGranary_farm_on_ruins(self):
        grid = create_base_grid()
        grid[1][5] = "farm"
        grid[2][1] = "farm"
        grid[2][8] = "farm"
        self.assertEqual(scoringCards.goldenGranary(grid), 9)

    def test_shoresideExpanse_isolated_clusters(self):
        grid = create_base_grid()
        grid[5][5] = "farm"
        grid[5][6] = "farm"
        grid[6][5] = "farm"
        grid[6][6] = "farm"
        grid[3][3] = "water"
        grid[3][4] = "water"
        grid[4][3] = "water"
        grid[4][4] = "water"
        self.assertEqual(scoringCards.shoresideExpanse(grid), 6)  # 2 clusters × 3

    def test_shoresideExpanse_adjacent_to_edge(self):
        grid = create_base_grid()
        grid[0][0] = "farm"
        grid[10][10] = "water"
        self.assertEqual(scoringCards.shoresideExpanse(grid), 0)

    def test_shoresideExpanse_adjacent_to_opposite_type(self):
        grid = create_base_grid()
        grid[5][5] = "farm"
        grid[5][6] = "water"  # adjacent
        grid[3][3] = "water"
        grid[3][4] = "farm"  # adjacent
        self.assertEqual(scoringCards.shoresideExpanse(grid), 0)

    def test_canalLake_mutual_adjacency(self):
        grid = create_base_grid()
        grid[5][5] = "farm"
        grid[5][6] = "water"
        grid[6][5] = "water"
        grid[6][6] = "farm"
        self.assertEqual(scoringCards.canalLake(grid), 4)

    def test_canalLake_no_adjacency(self):
        grid = create_base_grid()
        grid[0][0] = "farm"
        grid[10][10] = "water"
        self.assertEqual(scoringCards.canalLake(grid), 0)

    def test_magesValley_water_and_farm_adjacent_to_mountain(self):
        grid = create_base_grid()
        grid[5][5] = "mountain"
        grid[5][4] = "water"
        grid[5][6] = "farm"
        grid[4][5] = "farm"
        grid[6][5] = "water"
        self.assertEqual(scoringCards.magesValley(grid), 6)  # 2 water × 2 + 2 farm × 1

    def test_magesValley_no_adjacency(self):
        grid = create_base_grid()
        grid[0][0] = "water"
        grid[10][10] = "farm"
        self.assertEqual(scoringCards.magesValley(grid), 0)

class TestVillageScoring(unittest.TestCase):

    def test_greengoldPlains_single_cluster_with_3_terrains(self):
        grid = create_base_grid()
        grid[5][5] = "village"
        grid[5][6] = "village"
        grid[4][5] = "forest"
        grid[6][5] = "farm"
        grid[5][4] = "water"
        self.assertEqual(scoringCards.greengoldPlains(grid), 3)

    def test_greengoldPlains_cluster_with_2_terrains(self):
        grid = create_base_grid()
        grid[5][5] = "village"
        grid[5][6] = "village"
        grid[4][5] = "forest"
        grid[6][5] = "forest"
        self.assertEqual(scoringCards.greengoldPlains(grid), 0)

    def test_shieldgate_two_clusters(self):
        grid = create_base_grid()
        for i in range(6):
            grid[1][i] = "village"  # size 6
        for i in range(4):
            grid[3][i] = "village"  # size 4
        self.assertEqual(scoringCards.shieldgate(grid), 8)  # 4 × 2

    def test_shieldgate_one_cluster(self):
        grid = create_base_grid()
        for i in range(5):
            grid[5][i] = "village"
        self.assertEqual(scoringCards.shieldgate(grid), 0)

    def test_greatCity_largest_cluster_not_adjacent_to_mountain(self):
        grid = create_base_grid()
        for i in range(4):
            grid[5][i] = "village"
        self.assertEqual(scoringCards.greatCity(grid), 4)

    def test_greatCity_largest_cluster_adjacent_to_mountain(self):
        grid = create_base_grid()
        for i in range(5):
            grid[5][i] = "village"
        grid[5][5] = "mountain"  # adjacent to (5,4)
        self.assertEqual(scoringCards.greatCity(grid), 0)

    def test_wildholds_cluster_of_6(self):
        grid = create_base_grid()
        for i in range(6):
            grid[5][i] = "village"
        self.assertEqual(scoringCards.wildholds(grid), 8)

    def test_wildholds_two_clusters_of_6(self):
        grid = create_base_grid()
        for i in range(6):
            grid[1][i] = "village"
            grid[3][i] = "village"
        self.assertEqual(scoringCards.wildholds(grid), 16)

    def test_wildholds_cluster_of_5(self):
        grid = create_base_grid()
        for i in range(5):
            grid[5][i] = "village"
        self.assertEqual(scoringCards.wildholds(grid), 0)

class TestMiscScoring(unittest.TestCase):

    def test_borderlands_full_row_and_column(self):
        grid = create_base_grid()
        grid[0] = ["x"] * 11  # full row
        for r in range(11):
            grid[r][0] = "x"  # full column
        self.assertEqual(scoringCards.borderlands(grid), 12)  # 1 row + 1 col = 2 × 6

    def test_borderlands_multiple_rows_and_columns(self):
        grid = create_base_grid()
        for i in range(3):
            grid[i] = ["x"] * 11
        for c in range(2):
            for r in range(11):
                grid[r][c] = "x"
        self.assertEqual(scoringCards.borderlands(grid), (3 + 2) * 6)

    def test_borderlands_no_full_lines(self):
        grid = create_base_grid()
        grid[0][0] = "x"
        self.assertEqual(scoringCards.borderlands(grid), 0)

    def test_brokenRoad_single_diagonal(self):
        grid = create_base_grid()
        for i in range(11):
            grid[10 - i][i] = "x"  # bottom-left to top-right
        self.assertEqual(scoringCards.brokenRoad(grid), 1 * 3)

    def test_brokenRoad_multiple_diagonals(self):
        grid = create_base_grid()
        for start in range(5, 11):
            r, c = start, 0
            while r >= 0 and c < 11:
                grid[r][c] = "x"
                r -= 1
                c += 1
        self.assertEqual(scoringCards.brokenRoad(grid), 6 * 3)

    def test_brokenRoad_no_diagonals(self):
        grid = create_base_grid()
        self.assertEqual(scoringCards.brokenRoad(grid), 0)

    def test_cauldrons_surrounded_empty(self):
        grid = create_base_grid()
        grid[5][5] = 0
        grid[4][5] = "x"
        grid[6][5] = "x"
        grid[5][4] = "x"
        grid[5][6] = "x"
        self.assertEqual(scoringCards.cauldrons(grid), 1)

    def test_cauldrons_not_surrounded(self):
        grid = create_base_grid()
        grid[5][5] = 0
        grid[4][5] = 0
        grid[6][5] = "x"
        grid[5][4] = "x"
        grid[5][6] = "x"
        self.assertEqual(scoringCards.cauldrons(grid), 0)

    def test_lostBarony_3x3_square(self):
        grid = create_base_grid()
        for r in range(3):
            for c in range(3):
                grid[r][c] = "x"
        self.assertEqual(scoringCards.lostBarony(grid), 3 * 3)

    def test_lostBarony_5x5_square(self):
        grid = create_base_grid()
        for r in range(5):
            for c in range(5):
                grid[r][c] = "x"
        self.assertEqual(scoringCards.lostBarony(grid), 5 * 3)

    def test_lostBarony_no_square(self):
        grid = create_base_grid()
        grid[0][0] = "x"
        self.assertEqual(scoringCards.lostBarony(grid), 3)

if __name__ == '__main__':
    unittest.main()