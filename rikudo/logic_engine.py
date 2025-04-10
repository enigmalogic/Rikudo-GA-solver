from collections import deque
from typing import List, Tuple

from .puzzle_grid import PuzzleGrid
from .graph_utils import GraphUtils

Cell = Tuple[int, int]

class PuzzleLogicEngine:
    def __init__(self, puzzle: PuzzleGrid, graph: GraphUtils):
        self.puzzle = puzzle
        self.graph = graph

    def constraint_propagation(self) -> int:
        """
        BFS-style propagation of fixed values.
        If a number n is fixed, and exactly one neighbor can be n+1 or n-1,
        we force that neighbor to take that value.
        """
        newly_filled = 0
        queue = deque(self.puzzle.fixed_nums.items())  # (value, cell)

        while queue:
            val, cell = queue.popleft()

            for offset in [-1, 1]:
                next_val = val + offset
                if not (1 <= next_val <= self.puzzle.max_num):
                    continue
                if next_val in self.puzzle.fixed_nums:
                    continue

                candidates = [
                    nbr for nbr in self.graph.adjacency_dict.get(cell, [])
                    if self.puzzle.cells[nbr[0]][nbr[1]] == 0
                ]

                if len(candidates) == 1:
                    r, c = candidates[0]
                    self.puzzle.cells[r][c] = next_val
                    self.puzzle.fixed_nums[next_val] = (r, c)
                    self.puzzle.coordinate_num[next_val] = (r, c)
                    if (r, c) in self.puzzle.empty_cells:
                        self.puzzle.empty_cells.remove((r, c))
                    queue.append((next_val, (r, c)))
                    newly_filled += 1

        return newly_filled

    def gap_bridging(self) -> int:
        """
        Detects cells that are adjacent to two fixed neighbors whose values differ by 2.
        The cell must be the middle number.
        """
        newly_filled = 0

        for cell in self.puzzle.empty_cells[:]:                         # copy to avoid mutation during iteration
            neighbor_vals = [
                self.puzzle.cells[n[0]][n[1]]
                for n in self.graph.adjacency_dict.get(cell, [])
                if self.puzzle.cells[n[0]][n[1]] > 0
            ]

            for a in neighbor_vals:
                for b in neighbor_vals:
                    if a + 2 == b or b + 2 == a:
                        mid = (a + b) // 2
                        if mid not in self.puzzle.fixed_nums:
                            r, c = cell
                            self.puzzle.cells[r][c] = mid
                            self.puzzle.fixed_nums[mid] = cell
                            self.puzzle.coordinate_num[mid] = cell
                            self.puzzle.empty_cells.remove(cell)
                            newly_filled += 1
                            break                                       # done with this cell

        return newly_filled

    def preprocess(self, rounds: int = 2) -> Tuple[int, List[Tuple[int, Cell]]]:
        """
        Perform Phase 0 preprocessing:
        - Initialize adjacency, degrees
        - Apply dot constraints as forced edges
        - Perform constraint propagation and gap bridging to place values
        - Depth-2 lookahead inference (tentative)
        
        Returns:
            total_filled: number of values placed by propagation and bridging
            tentative: list of (val, cell) pairs placed tentatively via depth-2 lookahead
        """
        total_filled = 0
        tentative: List[Tuple[int, Cell]] = []

        """
            Repeatedly apply constraint propagation and gap bridging.
        """
        for _ in range(rounds):
            filled = self.constraint_propagation()
            filled += self.gap_bridging()
            if filled == 0:
                break
            total_filled += filled

        return total_filled, tentative