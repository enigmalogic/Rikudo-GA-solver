from collections import deque
from typing import Dict, List, Tuple

from .puzzle_grid import PuzzleGrid

Cell = Tuple[int, int]

class GraphUtils:
    def __init__(self, puzzle: PuzzleGrid):
        self.puzzle = puzzle
        self.adjacency_dict: Dict[Cell, List[Cell]] = {}
        self.pairwise_distances: Dict[Tuple[Cell, Cell], int] = {}
        self.degrees: Dict[Cell, int] = {}

        self.build_adjacency_dict()
        self.build_degrees()
        self.calculate_pairwise_distances()

    def build_adjacency_dict(self) -> None:
        self.adjacency_dict.clear()
        for r in range(self.puzzle.row_count):
            for c in range(len(self.puzzle.cells[r])):
                if self.puzzle.is_valid_cell(r, c):
                    cell = (r, c)
                    self.adjacency_dict[cell] = self.puzzle.neighbours(cell)

    def build_degrees(self) -> None:
        """Calculate self.degrees based on adjacency_dict."""
        self.degrees = {
            cell: len(neighbors)
            for cell, neighbors in self.adjacency_dict.items()
        }

    def bfs_from(self, src: Cell) -> Dict[Cell, int]:
        visited = {src: 0}
        queue = deque([src])
        while queue:
            current = queue.popleft()
            for neighbor in self.adjacency_dict.get(current, []):
                if neighbor not in visited:
                    visited[neighbor] = visited[current] + 1
                    queue.append(neighbor)
        return visited

    def calculate_pairwise_distances(self) -> None:
        """
        Efficiently compute BFS distances between all relevant cells:
        fixed + empty.
        """
        self.pairwise_distances.clear()
        relevant = list(self.puzzle.fixed_nums.values()) + self.puzzle.empty_cells

        for src in relevant:
            distances = self.bfs_from(src)
            for dst in relevant:
                if dst == src:
                    self.pairwise_distances[(src, dst)] = 0
                elif dst in distances:
                    d = distances[dst]
                    self.pairwise_distances[(src, dst)] = d
                    self.pairwise_distances[(dst, src)] = d
                else:
                    self.pairwise_distances[(src, dst)] = -1
                    self.pairwise_distances[(dst, src)] = -1
