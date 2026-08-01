"""
square_root_generator.py

Generates square root based aptitude questions.
"""

from __future__ import annotations

import math
import random
from typing import List

from src.config import settings
from src.models.enums import Difficulty, QuestionType
from src.models.question import Question
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


class SquareRootGenerator:
    """
    Generates aptitude questions related to square roots.
    """

    def __init__(self) -> None:
        """
        Initialize square root generator.
        """

        self.question_count = (
            settings.questions.square_root_questions
        )

        self.perfect_root_count = (
            settings.questions.perfect_square_roots
        )

        self.non_perfect_root_count = (
            settings.questions.non_perfect_square_roots
        )

        self.minimum = (
            settings.ranges.perfect_square_root_min
        )

        self.maximum = (
            settings.ranges.perfect_square_root_max
        )


    def generate(self) -> List[Question]:
        """
        Generate square root questions.

        Returns:
            List[Question]:
                Generated square root questions.
        """

        questions: List[Question] = []

        questions.extend(
            self._generate_perfect_square_roots()
        )

        questions.extend(
            self._generate_non_perfect_square_roots()
        )


        LOGGER.info(
            "Generated %s square root questions.",
            len(questions),
        )


        return questions[: self.question_count]



    def _generate_perfect_square_roots(
        self,
    ) -> List[Question]:
        """
        Generate perfect square root questions.

        Returns:
            List[Question]:
                Perfect square root questions.
        """

        questions: List[Question] = []

        used_numbers: set[int] = set()


        while len(questions) < self.perfect_root_count:

            number = random.randint(
                self.minimum,
                self.maximum,
            )


            if number in used_numbers:
                continue


            used_numbers.add(number)


            square = number ** 2


            questions.append(
                Question(
                    id=len(questions) + 1,

                    question_type=(
                        QuestionType.SQUARE_ROOT
                    ),

                    difficulty=(
                        self._get_difficulty(number)
                    ),

                    # Updated aptitude sheet style
                    question=(
                        f"√{square} = ?"
                    ),

                    answer=str(
                        number
                    ),

                    explanation=(
                        f"√{square} = {number}"
                    ),

                    topic="Square Roots",
                )
            )


        return questions



    def _generate_non_perfect_square_roots(
        self,
    ) -> List[Question]:
        """
        Generate non-perfect square root questions.

        Returns:
            List[Question]:
                Non-perfect square root questions.
        """

        questions: List[Question] = []

        minimum = (
            self.minimum ** 2
        )

        maximum = (
            self.maximum ** 2
        )


        while len(questions) < self.non_perfect_root_count:

            number = random.randint(
                minimum,
                maximum,
            )


            root = math.sqrt(number)


            if root.is_integer():
                continue


            questions.append(
                Question(
                    id=(
                        self.perfect_root_count
                        + len(questions)
                        + 1
                    ),

                    question_type=(
                        QuestionType.SQUARE_ROOT
                    ),

                    difficulty=(
                        Difficulty.HARD
                    ),

                    # Updated aptitude sheet style
                    question=(
                        f"√{number} = ?"
                    ),

                    answer=(
                        f"{root:.2f}"
                    ),

                    explanation=(
                        f"√{number} ≈ {root:.2f}"
                    ),

                    topic="Square Roots",
                )
            )


        return questions



    @staticmethod
    def _get_difficulty(
        number: int,
    ) -> Difficulty:
        """
        Determine difficulty level.

        Args:
            number:
                Root value.

        Returns:
            Difficulty:
                Difficulty category.
        """

        if number <= 20:

            return Difficulty.EASY


        if number <= 40:

            return Difficulty.MEDIUM


        return Difficulty.HARD