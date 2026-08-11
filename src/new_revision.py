"""
new_revision.py

Weekly revision generator for the
Daily Aptitude Generator.

Sunday workflow:

    1. Load the active history accumulated during
       Monday through Saturday.
    2. Select revision questions category-wise.
    3. Generate exactly 75 revision questions.
    4. Create question and answer PDFs.
    5. Return the generated PDF paths.

Important:
    No new aptitude questions are generated on the
    revision day.

    All Sunday questions come from the active history
    accumulated during the previous six days.

    History cleanup must happen only after the complete
    revision workflow has succeeded.
"""

from __future__ import annotations

import random

from pathlib import Path
from typing import List, Tuple

from src.config import settings
from src.models.answer import Answer
from src.models.enums import QuestionType
from src.models.question import Question
from src.pdf.answer_pdf import AnswerPDFGenerator
from src.pdf.question_pdf import QuestionPDFGenerator
from src.utils.history import HistoryManager
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


class WeeklyRevisionGenerator:
    """
    Generates the Sunday weekly revision paper.

    The revision paper contains exactly 75 questions
    selected from the previous six days of history.

    Distribution:

        Squares             10
        Cubes               10
        Square Roots        10
        Cube Roots           10
        Simplification      20
        Number Series       15

        Total               75
    """

    # =========================================================
    # REVISION DISTRIBUTION
    # =========================================================

    REVISION_DISTRIBUTION = {
        QuestionType.SQUARE: (
            settings.questions.square_questions
        ),

        QuestionType.CUBE: (
            settings.questions.cube_questions
        ),

        QuestionType.SQUARE_ROOT: (
            settings.questions.square_root_questions
        ),

        QuestionType.CUBE_ROOT: (
            settings.questions.cube_root_questions
        ),

        QuestionType.SIMPLIFICATION: (
            settings.questions.simplification_questions
        ),

        QuestionType.NUMBER_SERIES: (
            settings.questions.series_questions
        ),
    }

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self) -> None:
        """
        Initialize weekly revision services.
        """

        self.history = HistoryManager()

        self.question_pdf = (
            QuestionPDFGenerator()
        )

        self.answer_pdf = (
            AnswerPDFGenerator()
        )

    # =========================================================
    # MAIN REVISION WORKFLOW
    # =========================================================

    def generate(
        self,
    ) -> Tuple[Path, Path]:
        """
        Generate the complete Sunday revision paper.

        Returns:
            Tuple[Path, Path]:
                Question PDF path and answer PDF path.

        Raises:
            RuntimeError:
                If the six-day history does not contain
                enough questions for the required revision
                distribution.
        """

        LOGGER.info(
            "Starting weekly revision generation."
        )

        revision_questions = (
            self._select_revision_questions()
        )

        self._reassign_ids(
            revision_questions
        )

        LOGGER.info(
            "Selected %s revision questions.",
            len(revision_questions),
        )

        answers = (
            self._create_answers(
                revision_questions
            )
        )

        output_dir = (
            settings.paths.output_dir
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        question_pdf_path = (
            output_dir
            / self._revision_question_pdf_name()
        )

        answer_pdf_path = (
            output_dir
            / self._revision_answer_pdf_name()
        )

        # -----------------------------------------------------
        # Generate both PDFs.
        #
        # History is NOT cleaned here.
        # Cleanup is performed only after both operations
        # complete successfully.
        # -----------------------------------------------------

        self.question_pdf.generate(
            revision_questions,
            question_pdf_path,
        )

        self.answer_pdf.generate(
            answers,
            answer_pdf_path,
        )

        LOGGER.info(
            "Weekly revision PDFs generated successfully."
        )

        return (
            question_pdf_path,
            answer_pdf_path,
        )

    # =========================================================
    # GENERATE AND CLEANUP
    # =========================================================

    def generate_and_cleanup(
        self,
    ) -> Tuple[Path, Path]:
        """
        Generate the Sunday revision paper and clean
        active history after successful PDF generation.

        Cleanup happens ONLY after both the question PDF
        and answer PDF have been generated successfully.

        Returns:
            Tuple[Path, Path]:
                Question PDF path and answer PDF path.
        """

        question_pdf, answer_pdf = (
            self.generate()
        )

        LOGGER.info(
            "Revision paper generated successfully. "
            "Starting history cleanup."
        )

        self.history.cleanup_after_review()

        LOGGER.info(
            "Weekly revision workflow completed. "
            "Active history cleaned."
        )

        return (
            question_pdf,
            answer_pdf,
        )

    # =========================================================
    # REVISION QUESTION SELECTION
    # =========================================================

    def _select_revision_questions(
        self,
    ) -> List[Question]:
        """
        Select revision questions from active history.

        Questions are selected independently for each
        category according to REVISION_DISTRIBUTION.

        No new questions are generated.

        Returns:
            List[Question]:
                Exactly 75 revision questions.

        Raises:
            RuntimeError:
                If active history does not contain enough
                questions for any required category.
        """

        history_questions = (
            self.history.weekly_questions()
        )

        if not history_questions:

            raise RuntimeError(
                "No question history is available "
                "for weekly revision."
            )

        selected_questions: List[
            Question
        ] = []

        for question_type, required_count in (
            self.REVISION_DISTRIBUTION.items()
        ):

            available_questions = [
                question
                for question
                in history_questions
                if question.question_type
                == question_type
            ]

            available_count = len(
                available_questions
            )

            LOGGER.info(
                "Revision pool for %s: %s questions. "
                "Required: %s.",
                question_type.value,
                available_count,
                required_count,
            )

            if available_count < required_count:

                raise RuntimeError(
                    "Insufficient history for weekly "
                    f"revision category "
                    f"'{question_type.value}'. "
                    f"Required {required_count}, "
                    f"but only {available_count} "
                    f"available."
                )

            selected = random.sample(
                available_questions,
                required_count,
            )

            selected_questions.extend(
                selected
            )

        expected_count = sum(
            self.REVISION_DISTRIBUTION.values()
        )

        if len(selected_questions) != expected_count:

            raise RuntimeError(
                "Weekly revision generated an "
                f"unexpected number of questions: "
                f"{len(selected_questions)}. "
                f"Expected {expected_count}."
            )

        # -----------------------------------------------------
        # Shuffle all categories so the Sunday paper does not
        # simply appear as six consecutive topic blocks.
        # -----------------------------------------------------

        random.shuffle(
            selected_questions
        )

        return selected_questions

    # =========================================================
    # IDS
    # =========================================================

    @staticmethod
    def _reassign_ids(
        questions: List[Question],
    ) -> None:
        """
        Assign sequential IDs to revision questions.

        The original history IDs are not reused in the
        Sunday paper.

        Sunday revision IDs are always:

            1 ... 75
        """

        for index, question in enumerate(
            questions,
            start=1,
        ):

            question.id = index

    # =========================================================
    # ANSWERS
    # =========================================================

    @staticmethod
    def _create_answers(
        questions: List[Question],
    ) -> List[Answer]:
        """
        Create answer objects corresponding to
        the revision questions.
        """

        answers: List[Answer] = []

        for question in questions:

            answers.append(
                Answer(
                    question_id=question.id,

                    question_type=(
                        question.question_type
                    ),

                    question=(
                        question.question
                    ),

                    answer=(
                        question.answer
                    ),
                )
            )

        return answers

    # =========================================================
    # OUTPUT FILE NAMES
    # =========================================================

    @staticmethod
    def _revision_question_pdf_name() -> str:
        """
        Return the Sunday revision question PDF name.
        """

        return "Weekly_Revision.pdf"

    @staticmethod
    def _revision_answer_pdf_name() -> str:
        """
        Return the Sunday revision answer PDF name.
        """

        return "Weekly_Revision_Answers.pdf"

