"""
new_revision.py

Weekly revision workflow for the
Daily Aptitude Generator.

Sunday workflow:

- Read questions generated during the previous six days.
- Select the configured number of questions from each topic.
- Generate the weekly revision question PDF.
- Generate the weekly revision answer PDF.
- Send both PDFs by email.
- Clear the six-day history only after the complete
  revision workflow succeeds.

No new questions are generated on Sunday.
"""

from __future__ import annotations

import random

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

from src.config import settings
from src.email.mailer import EmailSender
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
    Coordinates the complete Sunday weekly revision workflow.

    Sunday does not generate fresh questions.

    Instead, it selects questions from the previous
    six days of generated history.
    """

    REVISION_TITLE = "Weekly Aptitude Revision"

    REVISION_ANSWER_TITLE = (
        "Weekly Aptitude Revision Answer Key"
    )

    def __init__(self) -> None:
        """
        Initialize weekly revision services.
        """

        self.history = HistoryManager()

        self.question_pdf = QuestionPDFGenerator()

        self.answer_pdf = AnswerPDFGenerator()

        self.email_sender = EmailSender()

    # =====================================================
    # MAIN WORKFLOW
    # =====================================================

    def generate(self) -> Tuple[Path, Path]:
        """
        Generate the Sunday weekly revision PDFs.

        Returns:
            Tuple containing question PDF and answer PDF paths.

        Raises:
            RuntimeError:
                If insufficient historical questions exist.
        """

        LOGGER.info(
            "Starting weekly revision generation."
        )

        revision_questions = (
            self._select_revision_questions()
        )

        expected_count = (
            self._total_revision_question_count()
        )

        if len(revision_questions) != expected_count:

            raise RuntimeError(
                "Weekly revision generation produced "
                f"{len(revision_questions)} questions. "
                f"Expected {expected_count}."
            )

        self._reassign_ids(
            revision_questions
        )

        answers = self._create_answers(
            revision_questions
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

        # -------------------------------------------------
        # Generate question PDF
        # -------------------------------------------------

        self.question_pdf.generate(
            revision_questions,
            question_pdf_path,
            title=self.REVISION_TITLE,
        )

        # -------------------------------------------------
        # Generate answer PDF
        # -------------------------------------------------

        self.answer_pdf.generate(
            answers,
            answer_pdf_path,
            title=self.REVISION_ANSWER_TITLE,
        )

        LOGGER.info(
            "Weekly revision PDFs generated successfully."
        )

        return (
            question_pdf_path,
            answer_pdf_path,
        )

    # =====================================================
    # GENERATE AND SEND
    # =====================================================

    def generate_and_send(self) -> None:
        """
        Generate the revision PDFs, send them by email,
        and clear history only after successful completion.

        If generation or email fails, history is preserved.
        """

        question_pdf, answer_pdf = (
            self.generate()
        )

        # -------------------------------------------------
        # Send revision PDFs
        # -------------------------------------------------

        self.email_sender.send(
            [
                question_pdf,
                answer_pdf,
            ]
        )

        LOGGER.info(
            "Weekly revision email sent successfully."
        )

        # -------------------------------------------------
        # Cleanup only after the complete workflow
        # succeeds.
        # -------------------------------------------------

        self._cleanup_after_revision()

    # =====================================================
    # REVISION QUESTION SELECTION
    # =====================================================

    def _select_revision_questions(
        self,
    ) -> List[Question]:
        """
        Select exactly 75 questions from the previous
        six calendar days.

        Distribution:

            Squares          : 10
            Cubes            : 10
            Square Roots     : 10
            Cube Roots       : 10
            Simplification   : 20
            Number Series    : 15

        Total                : 75
        """

        previous_six_days = (
            self._get_previous_six_days()
        )

        LOGGER.info(
            "Selecting revision questions from "
            "previous six days: %s",
            ", ".join(
                day.strftime("%Y-%m-%d")
                for day in previous_six_days
            ),
        )

        history_questions = (
            self._questions_from_previous_six_days(
                previous_six_days
            )
        )

        LOGGER.info(
            "Found %s historical questions "
            "from previous six days.",
            len(history_questions),
        )

        required_counts = (
            self._revision_distribution()
        )

        questions_by_type = (
            self._group_by_question_type(
                history_questions
            )
        )

        selected_questions: List[Question] = []

        for question_type, required_count in (
            required_counts.items()
        ):

            available = (
                questions_by_type.get(
                    question_type,
                    [],
                )
            )

            if len(available) < required_count:

                raise RuntimeError(
                    "Insufficient historical questions "
                    f"for topic '{question_type.value}'. "
                    f"Required: {required_count}, "
                    f"available: {len(available)}."
                )

            selected = random.sample(
                available,
                required_count,
            )

            selected_questions.extend(
                selected
            )

            LOGGER.info(
                "Selected %s questions for %s.",
                required_count,
                question_type.value,
            )

        random.shuffle(
            selected_questions
        )

        return selected_questions

    # =====================================================
    # PREVIOUS SIX DAYS
    # =====================================================

    @staticmethod
    def _get_previous_six_days() -> List:
        """
        Return the six calendar dates immediately before today.

        On Sunday this returns:

            Monday
            Tuesday
            Wednesday
            Thursday
            Friday
            Saturday
        """

        today = datetime.now().date()

        return [
            today - timedelta(days=offset)
            for offset in range(6, 0, -1)
        ]

    # =====================================================
    # FILTER HISTORY
    # =====================================================

    def _questions_from_previous_six_days(
        self,
        days: List,
    ) -> List[Question]:
        """
        Filter the already-loaded history to the
        previous six calendar days.
        """

        valid_dates = set(days)

        questions: List[Question] = []

        for question in self.history.questions:

            created_date = (
                question.created_at.date()
            )

            if created_date in valid_dates:

                questions.append(
                    question
                )

        return questions

    # =====================================================
    # GROUP QUESTIONS
    # =====================================================

    @staticmethod
    def _group_by_question_type(
        questions: List[Question],
    ) -> Dict[
        QuestionType,
        List[Question],
    ]:
        """
        Group historical questions by question type.
        """

        grouped: Dict[
            QuestionType,
            List[Question],
        ] = {}

        for question in questions:

            grouped.setdefault(
                question.question_type,
                [],
            ).append(
                question
            )

        return grouped

    # =====================================================
    # DISTRIBUTION
    # =====================================================

    @staticmethod
    def _revision_distribution() -> Dict[
        QuestionType,
        int,
    ]:
        """
        Return the required Sunday revision distribution.
        """

        return {
            QuestionType.SQUARE: 10,
            QuestionType.CUBE: 10,
            QuestionType.SQUARE_ROOT: 10,
            QuestionType.CUBE_ROOT: 10,
            QuestionType.SIMPLIFICATION: 20,
            QuestionType.NUMBER_SERIES: 15,
        }

    @classmethod
    def _total_revision_question_count(
        cls,
    ) -> int:
        """
        Return total revision question count.
        """

        return sum(
            cls._revision_distribution().values()
        )

    # =====================================================
    # FILE NAMES
    # =====================================================

    @staticmethod
    def _revision_question_pdf_name() -> str:
        """
        Return revision question PDF filename.
        """

        return "Weekly_Revision.pdf"

    @staticmethod
    def _revision_answer_pdf_name() -> str:
        """
        Return revision answer PDF filename.
        """

        return "Weekly_Revision_Answers.pdf"

    # =====================================================
    # IDS
    # =====================================================

    @staticmethod
    def _reassign_ids(
        questions: List[Question],
    ) -> None:
        """
        Assign sequential IDs from 1 onward.
        """

        for index, question in enumerate(
            questions,
            start=1,
        ):

            question.id = index

    # =====================================================
    # ANSWERS
    # =====================================================

    @staticmethod
    def _create_answers(
        questions: List[Question],
    ) -> List[Answer]:
        """
        Create answer objects for revision questions.
        """

        answers: List[Answer] = []

        for question in questions:

            answers.append(
                Answer(
                    question_id=question.id,
                    question_type=(
                        question.question_type
                    ),
                    question=question.question,
                    answer=question.answer,
                )
            )

        return answers

    # =====================================================
    # CLEANUP
    # =====================================================

    def _cleanup_after_revision(
        self,
    ) -> None:
        """
        Clear the completed week's history.

        This is called only after:
            1. revision questions were selected,
            2. question PDF was generated,
            3. answer PDF was generated,
            4. email was sent successfully.
        """

        LOGGER.info(
            "Weekly revision completed successfully. "
            "Starting history cleanup."
        )

        self.history.cleanup_after_review()

        LOGGER.info(
            "Weekly revision history cleanup completed."
        )
