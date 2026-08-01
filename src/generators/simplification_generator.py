"""
simplification_generator.py

Generates simplification-based aptitude questions.

Patterns:
- Basic BODMAS
- Missing value
- Equation based
- Fraction / Decimal
- Approximation
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import List, Tuple, Callable

from src.config import settings
from src.models.enums import Difficulty, QuestionType
from src.models.question import Question
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


class SimplificationGenerator:
    """
    Generates simplification aptitude questions.
    """

    def __init__(self) -> None:

        self.question_count = (
            settings.questions.simplification_questions
        )

        self.minimum = (
            settings.ranges.simplification_min_operand
        )

        self.maximum = (
            settings.ranges.simplification_max_operand
        )

        self.generated: set[str] = set()


    # =========================================================
    # MAIN GENERATOR
    # =========================================================

    def generate(self) -> List[Question]:

        questions: List[Question] = []

        generators: List[Tuple[Callable, int]] = [

            (self._generate_basic_bodmas, 6),

            (self._generate_missing_value, 5),

            (self._generate_equation_based, 4),

            (self._generate_fraction_decimal, 3),

            (self._generate_approximation, 2),

        ]


        for generator, count in generators:

            for _ in range(count):

                question = self._create_question(
                    generator()
                )

                questions.append(question)


        random.shuffle(
            questions
        )


        questions = questions[
            : self.question_count
        ]


        LOGGER.info(
            "Generated %s simplification questions.",
            len(questions),
        )


        return questions


    # =========================================================
    # QUESTION BUILDER
    # =========================================================

    def _create_question(
        self,
        data: Tuple[str, str, Difficulty],
    ) -> Question:

        question, answer, difficulty = data


        return Question(

            id=0,

            question_type=(
                QuestionType.SIMPLIFICATION
            ),

            difficulty=difficulty,

            question=question,

            answer=str(answer),

            explanation=(
                f"{question} = {answer}"
            ),

            topic="Simplification",
        )


    # =========================================================
    # TYPE 1 : BASIC BODMAS
    # =========================================================

    def _generate_basic_bodmas(
        self,
    ) -> Tuple[str, str, Difficulty]:

        while True:

            a = self._number()
            b = self._number()
            c = random.randint(2, 20)

            op1 = random.choice(
                ["+", "-", "*", "/"]
            )

            op2 = random.choice(
                ["+", "-", "*", "/"]
            )


            if op2 == "/" and c == 0:
                continue


            expression = (
                f"{a} {op1} {b} {op2} {c}"
            )


            try:

                answer = self._safe_eval(
                    expression
                )

            except Exception:

                continue


            return (
                f"{expression} = ?",
                str(answer),
                Difficulty.MEDIUM,
            )


    # =========================================================
    # TYPE 2 : MISSING VALUE
    # =========================================================

    def _generate_missing_value(
        self,
    ) -> Tuple[str, str, Difficulty]:

        base = random.randint(
            20,
            100,
        )

        multiplier = random.randint(
            2,
            10,
        )


        answer = base


        if random.choice([True, False]):

            total = (
                base * multiplier
            )

            return (
                f"? × {multiplier} = {total}",
                str(answer),
                Difficulty.MEDIUM,
            )


        total = (
            base + multiplier
        )

        return (
            f"? + {multiplier} = {total}",
            str(answer),
            Difficulty.EASY,
        )


    # =========================================================
    # TYPE 3 : EQUATION BASED
    # =========================================================

    def _generate_equation_based(
        self,
    ) -> Tuple[str, str, Difficulty]:

        value = random.randint(
            10,
            50,
        )

        multiplier = random.randint(
            2,
            8,
        )


        result = (
            value * multiplier
        )


        return (

            f"? × {multiplier} = {result}",

            str(value),

            Difficulty.MEDIUM,

        )


    # =========================================================
    # TYPE 4 : FRACTION / DECIMAL
    # =========================================================

    def _generate_fraction_decimal(
        self,
    ) -> Tuple[str, str, Difficulty]:

        number = random.choice(
            [100, 200, 300, 400, 500]
        )

        fraction = random.choice(
            [
                "1/2",
                "1/4",
                "3/5",
                "2/5",
            ]
        )


        result = (
            Fraction(fraction)
            *
            number
        )


        expression = (
            f"{fraction} of {number}"
        )


        return (

            f"{expression} = ?",

            str(int(result)),

            Difficulty.MEDIUM,

        )


    # =========================================================
    # TYPE 5 : APPROXIMATION
    # =========================================================

    def _generate_approximation(
        self,
    ) -> Tuple[str, str, Difficulty]:

        number = random.choice(
            [
                (49.8, 20),
                (99.5, 10),
                (19.8, 50),
            ]
        )


        value = round(
            number[0] * number[1]
        )


        return (

            f"{number[0]} × {number[1]} ≈ ?",

            str(value),

            Difficulty.HARD,

        )


    # =========================================================
    # HELPERS
    # =========================================================

    def _number(self) -> int:

        return random.randint(
            self.minimum,
            self.maximum,
        )


    @staticmethod
    def _safe_eval(
        expression: str,
    ) -> int:

        allowed = {

            "+": lambda x, y: x + y,

            "-": lambda x, y: x - y,

            "*": lambda x, y: x * y,

            "/": lambda x, y: x / y,

        }


        tokens = expression.split()


        result = int(tokens[0])


        index = 1


        while index < len(tokens):

            operator = tokens[index]

            value = int(tokens[index + 1])


            result = int(
                allowed[operator](
                    result,
                    value,
                )
            )


            index += 2


        return result