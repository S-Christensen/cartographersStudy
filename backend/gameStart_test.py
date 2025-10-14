import unittest
import gameStart
import numpy as np
from copy import deepcopy

class DummyCard:
    def __init__(self, shapes):
        self.shapes = shapes

class TestGameLogic(unittest.TestCase):

    def test_player_initialization(self):
        p = gameStart.Player("P1")
        self.assertEqual(p.id, "P1")
        self.assertEqual(len(p.current_grid), 11)
        self.assertEqual(p.score, 0)
        self.assertFalse(p.flags["placed_this_turn"])

    def test_game_session_initialization(self):
        gs = gameStart.GameSession("S1")
        self.assertEqual(gs.id, "S1")
        self.assertEqual(gs.players, {})

    def test_check_orthogonal_neighbors_valid(self):
        grid = [["filled"] * 11 for _ in range(11)]
        grid[5][5] = "mountain"
        self.assertTrue(gameStart.check_orthogonal_neighbors(grid, 4, 5))

    def test_check_orthogonal_neighbors_invalid(self):
        grid = [["filled"] * 11 for _ in range(11)]
        grid[5][5] = "mountain"
        grid[4][5] = 0  # unfilled neighbor
        self.assertFalse(gameStart.check_orthogonal_neighbors(grid, 4, 5))

    def test_flip_and_rotate_variants(self):
        shape = np.array([[1, 0], [1, 1]])
        variants = gameStart.flip_and_rotate(shape)
        self.assertEqual(len(variants), 8)
        self.assertTrue(any(np.array_equal(v, shape) for v in variants))

    def test_get_placement_diff(self):
        prev = [[0]*3 for _ in range(3)]
        new = deepcopy(prev)
        new[1][1] = "forest"
        diff = gameStart.get_placement_diff(prev, new)
        self.assertEqual(diff, [(1, 1, "forest")])

    def test_normalize_diff(self):
        diff = [(2, 3, "forest"), (2, 4, "forest"), (3, 3, "forest")]
        norm = gameStart.normalize_diff(diff)
        expected = np.array([
            ["forest", "forest"],
            ["forest", 0]
        ])
        self.assertEqual(norm.shape, expected.shape)

    def test_matches_card_shape_true(self):
        shape = np.array([["forest", 0], ["forest", "forest"]])
        diff = [(0, 0, "forest"), (1, 0, "forest"), (1, 1, "forest")]
        self.assertTrue(gameStart.matches_card_shape(diff, [shape]))

    def test_matches_card_shape_false(self):
        shape = np.array([["forest", "forest"], [0, "forest"]])
        diff = [(0, 0, "forest"), (1, 1, "forest"), (2, 0, "forest")]
        self.assertFalse(gameStart.matches_card_shape(diff, [shape]))

    def test_placed_on_ruins_true(self):
        diff = [(1, 5, "forest")]
        self.assertTrue(gameStart.placed_on_ruins(diff))

    def test_placed_on_ruins_false(self):
        diff = [(0, 0, "forest")]
        self.assertFalse(gameStart.placed_on_ruins(diff))

    def test_validate_placement_valid(self):
        prev = [[0]*3 for _ in range(3)]
        new = deepcopy(prev)
        new[1][1] = "forest"
        card = DummyCard([np.array([["forest"]])])
        valid, msg = gameStart.validate_placement(prev, new, card, False)
        self.assertTrue(valid)
        self.assertEqual(msg, "Valid placement")

    def test_validate_placement_no_diff(self):
        grid = [[0]*3 for _ in range(3)]
        card = DummyCard([np.array([["forest"]])])
        valid, msg = gameStart.validate_placement(grid, grid, card, False)
        self.assertFalse(valid)
        self.assertEqual(msg, "No placement detected")

    def test_validate_placement_bad_shape(self):
        prev = [[0]*3 for _ in range(3)]
        new = deepcopy(prev)
        new[1][1] = "forest"
        card = DummyCard([np.array([["forest", "forest"]])])
        valid, msg = gameStart.validate_placement(prev, new, card, False)
        self.assertFalse(valid)
        self.assertEqual(msg, "Shape does not match card")

    def test_validate_placement_ruins_required(self):
        prev = [[0]*3 for _ in range(3)]
        new = deepcopy(prev)
        new[0][0] = "forest"
        card = DummyCard([np.array([["forest"]])])
        valid, msg = gameStart.validate_placement(prev, new, card, True)
        self.assertFalse(valid)
        self.assertEqual(msg, "Ruins card must be placed on a ruins tile")

    def test_monster_penalty(self):
        grid = [[0]*4 for _ in range(4)]
        grid[1][1] = "Monster"
        grid[2][2] = "Monster"
        penalty = gameStart.monster_penalty(grid)
        self.assertEqual(penalty, 6)

    def test_initialize_session(self):
        session = gameStart.initialize_session()
        self.assertEqual(session.id, "session_001")
        self.assertIn("player_1", session.players)

    def test_build_decks(self):
        deck, monster_deck = gameStart.build_decks()
        self.assertGreaterEqual(len(deck), 10)
        self.assertEqual(len(monster_deck), 4)
        self.assertTrue(all(
            card.name in ["GoblinAttack", "GnollRaid", "BugbearAssault", "KoboldOnslaught"] for card in monster_deck))

    def test_select_scoring_cards(self):
        score_types = gameStart.select_scoring_cards()
        self.assertEqual(len(score_types), 4)
        self.assertTrue(callable(score_types[0]))

    def test_run_season_valid_flow(self):
        session = gameStart.initialize_session()
        deck, monster_deck = gameStart.build_decks()
        score_types = gameStart.select_scoring_cards()
        print("\nDeck:")
        for i in deck:
            print(i.name)
        print("\nMonster Deck:")
        for i in monster_deck:
            print(i.name)

        print(score_types)

        gameStart.run_season(session, deck, monster_deck, score_types, 0)
        self.assertLessEqual(session.players["player_1"].score, 3)


if __name__ == "__main__":
    unittest.main()