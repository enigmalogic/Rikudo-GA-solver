from typing import List, Tuple, Dict, Union

Cell = Tuple[int, int]
Dot = Tuple[Cell, Cell]
Dots = List[Dot]

class PuzzleGrid:
    def __init__(
        self,
        max_num: int,
        dimensions: Tuple[int, int],
        cells: List[List[int]],
        dots: Dots,
        empty_cells: List[Cell],
        fixed_nums: Dict[int, Cell],
    ):
        self.cells: List[List[int]] = cells
        self.fixed_nums: Dict[int, Cell] = fixed_nums
        self.empty_cells: List[Cell] = empty_cells
        self.dots: Dots = dots
        self.max_num: int = max_num
        self.dot_count: int = len(dots)
        self.row_count, self.column_count = dimensions

        self.coordinate_num: Dict[int, Cell] = {}
        self.calculate_coordinates()

    def __str__(self):
        lines = [f"{self.row_count} {self.column_count} {self.max_num}"]
        for row in self.cells:
            lines.append(" ".join(map(str, row)))
        lines.append(str(self.dot_count))
        for (x1, y1), (x2, y2) in self.dots:
            lines.append(f"{x1} {y1} {x2} {y2}")
        return "\n".join(lines)

    @classmethod
    def parse(cls, puzzle_str: str) -> "PuzzleGrid":
        lines = puzzle_str.splitlines()
        row_count, col_count, max_num = map(int, lines[0].split())
        cells: List[List[int]] = []
        fixed_nums: Dict[int, Cell] = {}
        empty_cells: List[Cell] = []

        for i, line in enumerate(lines[1:row_count + 1]):
            row_vals = list(map(int, line.split()))
            row = []
            for j, val in enumerate(row_vals):
                row.append(val)
                if val == 0:
                    empty_cells.append((i, j))
                elif val > 0:
                    fixed_nums[val] = (i, j)
            cells.append(row)

        dot_count = int(lines[row_count + 1])
        dots: Dots = []
        for line in lines[row_count + 2:]:
            x1, y1, x2, y2 = map(int, line.split())
            dots.append(((x1, y1), (x2, y2)))

        return cls(max_num, (row_count, col_count), cells, dots, empty_cells, fixed_nums)

    def is_valid_cell(self, r: int, c: int) -> bool:
        return (
            0 <= r < self.row_count
            and 0 <= c < len(self.cells[r])
            and self.cells[r][c] >= 0
        )

    def neighbours(self, cell: Cell) -> List[Cell]:
        i, j = cell
        res = []

        if len(self.cells[i]) == self.column_count:  # full row
            if i > 0:
                if j > 0:
                    res.append((i - 1, j - 1))
                if j < self.column_count - 1:
                    res.append((i - 1, j))
            if i < self.row_count - 1:
                if j > 0:
                    res.append((i + 1, j - 1))
                if j < self.column_count - 1:
                    res.append((i + 1, j))
        else:  # short row
            if i > 0:
                res.append((i - 1, j))
                res.append((i - 1, j + 1))
            if i < self.row_count - 1:
                res.append((i + 1, j))
                res.append((i + 1, j + 1))

        if j > 0:
            res.append((i, j - 1))
        if j < len(self.cells[i]) - 1:
            res.append((i, j + 1))

        return [nbr for nbr in res if self.is_valid_cell(nbr[0], nbr[1])]

    def calculate_coordinates(self) -> None:
        self.coordinate_num = self.fixed_nums.copy()
        for i, j in self.empty_cells:
            val = self.cells[i][j]
            if val > 0:
                self.coordinate_num[val] = (i, j)

    def find_coordinates(self, value: int) -> Union[Cell, None]:
        return self.coordinate_num.get(value)

    def set_empty_cells(self, filled_cells: List[int]) -> None:
        for idx, val in enumerate(filled_cells):
            r, c = self.empty_cells[idx]
            self.cells[r][c] = val
        self.calculate_coordinates()