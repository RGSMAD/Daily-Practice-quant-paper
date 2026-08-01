"""
cube_root_generator.py

Generates cube root based aptitude questions.
"""

from __future__ import annotations

import random
from typing import List

from src.config import settings
from src.models.enums import Difficulty, QuestionType
from src.models.question import Question
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


class CubeRootGenerator:
    """
    Generates aptitude questions related to cube roots.
    """

    def __init__(self) -> None:
        """
        Initialize cube root generator.
        """

        self.question_count = (
            settings.questions.cube_root_questions
        )

        self.minimum = (
            settings.ranges.perfect_cube_root_min
        )

        self.maximum = (
            settings.ranges.perfect_cube_root_max
        )


    # =========================================================
    # MAIN GENERATOR
    # =========================================================

    def generate(self) -> List[Question]:
        """
        Generate cube root questions.

        Returns:
            List[Question]:
                Generated cube root questions.
        """

        questions: List[Question] = []

        generated_numbers: set[int] = set()


        while len(questions) < self.question_count:

            root_value = random.randint(
                self.minimum,
                self.maximum,
            )


            if root_value in generated_numbers:

                continue


            generated_numbers.add(
                root_value
            )


            cube_value = (
                root_value ** 3
            )


            questions.append(

                Question(

                    id=len(questions) + 1,


                    question_type=(

                        QuestionType.CUBE_ROOT

                    ),


                    difficulty=(

                        self._get_difficulty(
                            root_value
                        )

                    ),


                    # LaTeX cube root rendering
                    question=(

                        f"\\sqrt[3]{{{cube_value}}} = ?"

                    ),


                    answer=str(
                        root_value
                    ),


                    explanation=(

                        f"\\sqrt[3]{{{cube_value}}} = {root_value}"

                    ),


                    topic="Cube Roots",

                )

            )


        LOGGER.info(

            "Generated %s cube root questions.",

            len(questions),

        )


        return questions



    # =========================================================
    # DIFFICULTY
    # =========================================================

    @staticmethod
    def _get_difficulty(
        number: int,
    ) -> Difficulty:
        """
        Determine difficulty level.

        Args:
            number:
                Cube root value.

        Returns:
            Difficulty:
                Difficulty category.
        """

        if number <= 5:

            return Difficulty.EASY


        if number <= 12:

            return Difficulty.MEDIUM


        return Difficulty.HARD