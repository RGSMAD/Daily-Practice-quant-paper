"""
cube_generator.py

Generates cube-based aptitude questions.
"""

from __future__ import annotations

import random
from typing import List

from src.config import settings
from src.models.enums import Difficulty, QuestionType
from src.models.question import Question
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


class CubeGenerator:
    """
    Generates aptitude questions related to cubes.
    """

    def __init__(self) -> None:
        """
        Initialize cube generator.
        """

        self.question_count = (
            settings.questions.cube_questions
        )

        self.minimum = (
            settings.ranges.cube_min
        )

        self.maximum = (
            settings.ranges.cube_max
        )


    def generate(self) -> List[Question]:
        """
        Generate cube questions.

        Returns:
            List[Question]:
                Generated cube questions.
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


            cube_value = (
                number ** 3
            )


            question = Question(
                id=len(questions) + 1,

                question_type=(
                    QuestionType.CUBE
                ),

                difficulty=difficulty,

                question=(
                    f"What is the cube of {number}?"
                ),

                answer=str(
                    cube_value
                ),

                explanation=(
                    f"{number} × {number} × "
                    f"{number} = {cube_value}"
                ),

                topic="Cubes",
            )


            questions.append(question)


        LOGGER.info(
            "Generated %s cube questions.",
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
            Difficulty:
                Difficulty category.
        """

        if number <= 99:

            return Difficulty.EASY


        if number <= 499:

            return Difficulty.MEDIUM


        return Difficulty.HARD