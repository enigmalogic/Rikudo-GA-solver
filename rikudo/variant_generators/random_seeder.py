import copy
import random
from typing import List

from ..puzzle_grid import PuzzleGrid
from .base import PuzzleVariantGenerator

class RandomSeeder(PuzzleVariantGenerator):
    def __init__(self, puzzle: PuzzleGrid, seed: int = None):
        self.puzzle = puzzle
        self.random = random.Random(seed)

    def generate_variants(self, limit: int) -> List[PuzzleGrid]:
        variants = []
        missing_vals = [v for v in range(1, self.puzzle.max_num + 1) if v not in self.puzzle.fixed_nums]
        empty_cells = self.puzzle.empty_cells

        if len(missing_vals) > len(empty_cells):
            raise ValueError("More missing values than available empty cells!")

        for _ in range(limit):
            puzzle_copy = copy.deepcopy(self.puzzle)
            shuffled_values = missing_vals[:]
            self.random.shuffle(shuffled_values)

            for idx, val in enumerate(shuffled_values):
                r, c = puzzle_copy.empty_cells[idx]
                puzzle_copy.cells[r][c] = val
                puzzle_copy.fixed_nums[val] = (r, c)
                puzzle_copy.coordinate_num[val] = (r, c)

            puzzle_copy.empty_cells = puzzle_copy.empty_cells[len(shuffled_values):]
            variants.append(puzzle_copy)

        return variants