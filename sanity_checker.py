from rikudo.puzzle_grid import PuzzleGrid
from rikudo.graph_utils import GraphUtils
from rikudo.logic_engine import PuzzleLogicEngine
from rikudo.variant_generators.depth2_engine import Depth2Engine
from rikudo.variant_generators.random_seeder import RandomSeeder

from typing import List

def print_grid(puzzle: PuzzleGrid) -> None:
    print("=== Puzzle Grid ===")
    dot_cells = {a for a, _ in puzzle.dots} | {b for _, b in puzzle.dots}
    for r, row in enumerate(puzzle.cells):
        if len(row) < puzzle.column_count:
            print("  ", end="")  # indent short rows
        for c, val in enumerate(row):
            coord = (r, c)
            if val == -1:
                print("##", end=" ")
            elif val == 0:
                print(" D" if coord in dot_cells else " X", end=" ")
            else:
                print(f"{val:2}", end=" ")
        print()
    print("=== End of Grid ===\n")

def print_summary(puzzle: PuzzleGrid) -> None:
    print(f"Grid: {puzzle.row_count}×{puzzle.column_count}")
    print(f"Max value: {puzzle.max_num}")
    print(f"Fixed: {len(puzzle.fixed_nums)}, Empty: {len(puzzle.empty_cells)}, Dots: {puzzle.dot_count}")

if __name__ == "__main__":
    with open("input2.txt") as f:
        puzzle = PuzzleGrid.parse(f.read())

    print("=== 🧠 Initial Puzzle Summary ===")
    print_summary(puzzle)
    print_grid(puzzle)

    graph = GraphUtils(puzzle)
    logic = PuzzleLogicEngine(puzzle, graph)

    filled, _ = logic.preprocess(rounds=2)
    print(f"✅ Constraint propagation + gap bridging filled {filled} cells\n")

    print("=== 🔁 Updated Puzzle Grid ===")
    print_summary(puzzle)
    print_grid(puzzle)

    print("=== 🔍 Depth-2 Engine ===")
    depth2_engine = Depth2Engine(puzzle, graph)
    d2_candidates = depth2_engine.enumerate_candidates()
    total_perms = sum(len(v) for v in d2_candidates.values())
    print(f"Found depth-2 permutations for {len(d2_candidates)} (n, n+3) pairs")
    print(f"Total candidate permutations: {total_perms}")

    variants_d2 = depth2_engine.generate_variants(limit=5)
    print(f"Generated {len(variants_d2)} full board variants from Depth2Engine\n")

    for i, variant in enumerate(variants_d2):
        print(f"--- Variant {i + 1} (Depth-2) ---")
        print_grid(variant)

    print("=== 🎲 Random Seeder ===")
    rand_seeder = RandomSeeder(puzzle, seed=42)
    variants_rand = rand_seeder.generate_variants(limit=3)
    print(f"Generated {len(variants_rand)} full board variants from RandomSeeder\n")

    for i, variant in enumerate(variants_rand):
        print(f"--- Variant {i + 1} (Random) ---")
        print_grid(variant)

    with open("seed_depth2.txt", "w") as f:
        f.write(str(variants_d2[0]))
    print("📤 First Depth-2 variant written to seed_depth2.txt")

    with open("seed_random.txt", "w") as f:
        f.write(str(variants_rand[0]))
    print("📤 First Random variant written to seed_random.txt")