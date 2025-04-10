from abc import ABC, abstractmethod
from typing import List

from ..puzzle_grid import PuzzleGrid

class PuzzleVariantGenerator(ABC):
    @abstractmethod
    def generate_variants(self, limit: int) -> List[PuzzleGrid]:
        """
        Generate full puzzle variants that obey all rules.
        Intended to be used for seeding a Genetic Algorithm.

        Args:
            limit (int): maximum number of variants to return

        Returns:
            List[PuzzleGrid]: list of full puzzle board variants
        """
        pass