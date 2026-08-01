"""
square_generator.py

Generates square-based aptitude questions.
"""

from __future__ import annotations

import random
from typing import List

from src.config import settings
from src.models.enums import Difficulty, QuestionType
from src.models.question import Question
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


class SquareGenerator:
    """
    Generates aptitude questions related to squares.
    """

    def __init__(self) -> None:
        """
        Initialize square generator.
        """

        self.question_count = (
            settings.questions.square_questions
        )

        self.minimum = (
            settings.ranges.square_min
        )

        self.maximum = (
            settings.ranges.square_max
        )


    def generate(self) -> List[Question]:
        """
        Generate square questions.

        Returns:
            List[Question]:
                Generated square questions.
        """

        questions: List[Question] = []

        generated_numbers: set[int] = set()


        while len(questions) < self.question_count:

            number = random.randint(
                self.minimum,
                self.maximum,
            )


            if number in generated_numbers:
                continue


            generated_numbers.add(number)


            difficulty = (
                self._get_difficulty(number)
            )


            question = Question(
                id=len(questions) + 1,

                question_type=(
                    QuestionType.SQUARE
                ),

                difficulty=difficulty,

                # Updated aptitude sheet style
                question=(
                    f"{number}² = ?"
                ),

                answer=str(
                    number ** 2
                ),

                explanation=(
                    f"{number} × {number} = "
                    f"{number ** 2}"
                ),

                topic="Squares",
            )


            questions.append(question)


        LOGGER.info(
            "Generated %s square questions.",
            len(questions),
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
                Number used in question.

        Returns:
            Difficulty category.
        """

        if number <= 99:

            return Difficulty.EASY


        if number <= 499:

            return Difficulty.MEDIUM


        return Difficulty.HARD