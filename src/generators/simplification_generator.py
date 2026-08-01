"""
simplification_generator.py

Generates simplification-based aptitude questions.
"""

from __future__ import annotations

import random
from typing import List, Callable

from src.config import settings
from src.models.enums import Difficulty, QuestionType
from src.models.question import Question
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


class SimplificationGenerator:
    """
    Generates arithmetic simplification questions.
    """

    def __init__(self) -> None:
        """
        Initialize simplification generator.
        """

        self.question_count = (
            settings.questions.simplification_questions
        )

        self.minimum = (
            settings.ranges.simplification_min_operand
        )

        self.maximum = (
            settings.ranges.simplification_max_operand
        )

        self.operators: List[str] = [
            "+",
            "-",
            "*",
            "/",
        ]


    def generate(self) -> List[Question]:
        """
        Generate simplification questions.

        Returns:
            List[Question]:
                Generated simplification questions.
        """

        questions: List[Question] = []

        generated_expressions: set[str] = set()


        while len(questions) < self.question_count:

            expression, answer = (
                self._create_expression()
            )


            if expression in generated_expressions:

                continue


            generated_expressions.add(
                expression
            )


            questions.append(
                Question(
                    id=len(questions) + 1,

                    question_type=(
                        QuestionType.SIMPLIFICATION
                    ),

                    difficulty=(
                        self._get_difficulty(
                            expression
                        )
                    ),

                    question=(
                        f"Simplify: {expression}"
                    ),

                    answer=str(
                        answer
                    ),

                    explanation=(
                        f"{expression} = {answer}"
                    ),

                    topic="Simplification",
                )
            )


        LOGGER.info(
            "Generated %s simplification questions.",
            len(questions),
        )


        return questions



    def _create_expression(
        self,
    ) -> tuple[str, int]:
        """
        Create a mathematical expression.

        Returns:
            tuple[str, int]:
                Expression and calculated answer.
        """

        first = random.randint(
            self.minimum,
            self.maximum,
        )

        second = random.randint(
            self.minimum,
            self.maximum,
        )

        third = random.randint(
            2,
            20,
        )


        operator_one = random.choice(
            self.operators
        )

        operator_two = random.choice(
            self.operators
        )


        expression = (
            f"{first} "
            f"{operator_one} "
            f"{second} "
            f"{operator_two} "
            f"{third}"
        )


        answer = self._evaluate(
            first,
            second,
            third,
            operator_one,
            operator_two,
        )


        return expression, answer



    @staticmethod
    def _evaluate(
        first: int,
        second: int,
        third: int,
        operator_one: str,
        operator_two: str,
    ) -> int:
        """
        Evaluate arithmetic expression.

        Args:
            first:
                First operand.

            second:
                Second operand.

            third:
                Third operand.

            operator_one:
                First operator.

            operator_two:
                Second operator.

        Returns:
            int:
                Expression result.
        """

        expression = (
            f"{first}"
            f"{operator_one}"
            f"{second}"
            f"{operator_two}"
            f"{third}"
        )


        return int(
            eval(expression)
        )



    @staticmethod
    def _get_difficulty(
        expression: str,
    ) -> Difficulty:
        """
        Determine question difficulty.

        Args:
            expression:
                Generated expression.

        Returns:
            Difficulty:
                Difficulty category.
        """

        operator_count = (
            len(
                [
                    symbol
                    for symbol in expression
                    if symbol in "+-*/"
                ]
            )
        )


        if operator_count == 1:

            return Difficulty.EASY


        if operator_count == 2:

            return Difficulty.MEDIUM


        return Difficulty.HARD