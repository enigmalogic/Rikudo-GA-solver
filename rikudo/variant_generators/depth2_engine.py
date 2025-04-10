from typing import List, Tuple, Dict
from itertools import product
import copy

from ..puzzle_grid import PuzzleGrid
from ..graph_utils import GraphUtils
# from variant_generators.base import PuzzleVariantGenerator
from .base import PuzzleVariantGenerator

Cell = Tuple[int, int]

class Depth2Engine(PuzzleVariantGenerator):
    def __init__(self, puzzle: PuzzleGrid, graph: GraphUtils):
        self.puzzle = puzzle
        self.graph = graph
        self.adjacency = graph.adjacency_dict
        self.max_num = puzzle.max_num

    def enumerate_candidates(self) -> Dict[int, List[Tuple[int, Cell, int, Cell]]]:
        """
        For all (n, n+3) pairs where both n and n+3 are fixed, and n+1, n+2 not yet filled:
        1. We look for exactly TWO empty cells in between.
        2. Then we confirm that the second empty cell is adjacent to (n+3).
        3. We return both permutations: (n+1, cellA, n+2, cellB) and (n+1, cellB, n+2, cellA).

        This avoids counting the end cell as if it were empty and fixes the issue
        where BFS might produce partial paths that inadvertently include n+3 in the 'middle'.
        """
        results: Dict[int, List[Tuple[int, Cell, int, Cell]]] = {}

        for n in range(1, self.max_num - 2):
            if n in self.puzzle.fixed_nums and (n + 3) in self.puzzle.fixed_nums:
                # Must not have already placed n+1 or n+2
                if (n + 1) in self.puzzle.fixed_nums or (n + 2) in self.puzzle.fixed_nums:
                    continue

                start = self.puzzle.fixed_nums[n]           # cell for n
                end = self.puzzle.fixed_nums[n + 3]         # cell for n+3

                # We do BFS tracking exactly how many empty cells we've used in 'path'
                queue = [(start, [])]                       # (currentCell, list_of_empty_cells_visited)
                valid_paths = []

                while queue:
                    current, epath = queue.pop(0)

                    # If we've used exactly 2 empty cells so far,
                    # check if we can directly reach 'end' from 'current'
                    if len(epath) == 2:
                        if end in self.adjacency[current]:
                            # We found a path of 2 empty cells that leads to n+3
                            valid_paths.append(epath)
                        # No need to expand further
                        continue
                    
                    # Otherwise, we can expand BFS to other empty neighbors (excluding end)
                    for nbr in self.adjacency[current]:
                        if nbr == start or nbr == end:
                            # We skip going directly to 'end' or back to 'start' mid-path
                            continue
                        if nbr in epath:
                            continue
                        # We only move onto an empty cell
                        if self.puzzle.cells[nbr[0]][nbr[1]] == 0:
                            queue.append((nbr, epath + [nbr]))

                seen = set()
                candidates = []
                for path in valid_paths:
                    # Create a sorted key so that (c1, c2) always appears as (min, max)
                    sorted_key = tuple(sorted(path))
                    if sorted_key in seen:
                        continue
                    seen.add(sorted_key)
                    # Generate both candidate mappings
                    mapping1 = (n + 1, path[0], n + 2, path[1])
                    mapping2 = (n + 1, path[1], n + 2, path[0])
                    # Check validity for each mapping:
                    # mapping1 is valid if the cell for n+1 is adjacent to start and the cell for n+2 is adjacent to end.
                    if (mapping1[1] in self.adjacency[start] and
                        mapping1[3] in self.adjacency[end]):
                        candidates.append(mapping1)
                    if (mapping2[1] in self.adjacency[start] and
                        mapping2[3] in self.adjacency[end]):
                        candidates.append(mapping2)

                if candidates:
                    results[n] = candidates

        return results

    # This will take a list of (value, cell) pairs and apply them to a Puzzle instance
    def apply_assignments(self, puzzle: PuzzleGrid, assignments: List[Tuple[int, Cell]]) -> None:
        for val, cell in assignments:
            # Duplicate Cell Assignment Guard
            if val in puzzle.fixed_nums:
                continue                                    # This number has already been placed
            if puzzle.cells[cell[0]][cell[1]] != 0:
                continue                                    # This cell is already occupied
            r, c = cell
            puzzle.cells[r][c] = val
            puzzle.fixed_nums[val] = cell
            puzzle.coordinate_num[val] = cell
            if cell in puzzle.empty_cells:
                puzzle.empty_cells.remove(cell)

    # This will assign any remaining unplaced numbers to empty cells, prioritizing adjacency to n+1 and n-1
    def greedy_fill_remaining(self, puzzle: PuzzleGrid) -> int:
        filled = 0
        missing_vals = [v for v in range(1, puzzle.max_num + 1) if v not in puzzle.fixed_nums]

        for val in missing_vals:
            candidates = []

            for neighbor_val in (val - 1, val + 1):
                if 1 <= neighbor_val <= puzzle.max_num and neighbor_val in puzzle.fixed_nums:
                    neighbor_cell = puzzle.fixed_nums[neighbor_val]
                    for nbr in self.adjacency.get(neighbor_cell, []):
                        if puzzle.cells[nbr[0]][nbr[1]] == 0:
                            candidates.append(nbr)

            if not candidates:
                # Fallback: pick any remaining empty cell
                candidates = list(puzzle.empty_cells)

            if not candidates:
                continue

            chosen = candidates[0]
            r, c = chosen
            puzzle.cells[r][c] = val
            puzzle.fixed_nums[val] = chosen
            puzzle.coordinate_num[val] = chosen
            puzzle.empty_cells.remove(chosen)
            filled += 1

        return filled

    def generate_variants(self, limit: int = 1000) -> List[PuzzleGrid]:
        candidates = self.enumerate_candidates()
        keys = sorted(candidates.keys())
        choices = [candidates[k] for k in keys]

        all_variants = []
        count = 0

        for combo in product(*choices):
            if count >= limit:
                break
            
            # Flatten [(n+1, cellA, n+2, cellB), ...] → [(n+1, cellA), (n+2, cellB), ...]
            flat_assignments = [item for quad in combo for item in [(quad[0], quad[1]), (quad[2], quad[3])]]
            # Deep copy puzzle and apply
            puzzle_copy = copy.deepcopy(self.puzzle)
            self.apply_assignments(puzzle_copy, flat_assignments)
            self.greedy_fill_remaining(puzzle_copy)

            all_variants.append(puzzle_copy)
            count += 1

        return all_variants