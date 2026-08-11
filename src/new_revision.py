
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

    # =========================================================
    # REVISION CONFIGURATION
    # =========================================================

    REVISION_TITLE = "Weekly Aptitude Revision"

    REVISION_ANSWER_TITLE = (
        "Weekly Aptitude Revision Answer Key"
    )

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self) -> None:
        """
        Initialize weekly revision services.
        """

        self.history = HistoryManager()

        self.question_pdf = QuestionPDFGenerator()

        self.answer_pdf = AnswerPDFGenerator()

        self.email_sender = EmailSender()

    # =========================================================
    # MAIN WORKFLOW
    # =========================================================

    def generate(
        self,
    ) -> Tuple[Path, Path]:
        """
        Generate the Sunday weekly revision PDFs.

        Returns:
            Tuple[Path, Path]:
                Revision question PDF path and
                revision answer PDF path.

        Raises:
            RuntimeError:
                If the six-day history does not contain
                enough questions for the complete revision.
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
        # Generate revision question PDF
        # -----------------------------------------------------

        self.question_pdf.generate(
            revision_questions,
            question_pdf_path,
            title=self.REVISION_TITLE,
        )

        # -----------------------------------------------------
        # Generate revision answer PDF
        # -----------------------------------------------------

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

    # =========================================================
    # GENERATE AND SEND
    # =========================================================

    def generate_and_send(
        self,
    ) -> None:
        """
        Generate and send the Sunday revision paper.

        History is cleared ONLY after:
        - revision questions are selected,
        - both PDFs are generated,
        - email is successfully sent.

        If any step fails, history remains untouched.
        """

        question_pdf, answer_pdf = (
            self.generate()
        )

        # -----------------------------------------------------
        # Send revision paper
        # -----------------------------------------------------

        self.email_sender.send(
            [
                question_pdf,
                answer_pdf,
            ],
            subject=(
                "Weekly Aptitude Revision"
            ),
            body=(
                "Hello,\n\n"
                "Please find this week's aptitude "
                "revision paper attached.\n\n"
                "Happy Learning!"
            ),
        )

        LOGGER.info(
            "Weekly revision email completed successfully."
        )

        # -----------------------------------------------------
        # IMPORTANT:
        #
        # History is cleared only after the complete workflow
        # succeeds.
        #
        # This starts the history cycle for the next week.
        # -----------------------------------------------------

        self._cleanup_after_revision()

    # =========================================================
    # REVISION QUESTION SELECTION
    # =========================================================

    def _select_revision_questions(
        self,
    ) -> List[Question]:
        """
        Select revision questions from the previous
        six calendar days.

        The required distribution is:

        Squares             : 10
        Cubes               : 10
        Square Roots        : 10
        Cube Roots          : 10
        Simplification      : 20
        Number Series       : 15

        Total                : 75

        No newly generated questions are used.
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
            "Found %s questions in previous "
            "six days of history.",
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
                    "Insufficient history for weekly "
                    f"revision topic "
                    f"'{question_type.value}'. "
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
                "Weekly revision selected %s "
                "questions for %s.",
                required_count,
                question_type.value,
            )

        # -----------------------------------------------------
        # Shuffle the complete 75-question paper so that
        # sections are not simply grouped by generator.
        # -----------------------------------------------------

        random.shuffle(
            selected_questions
        )

        return selected_questions

    # =========================================================
    # PREVIOUS SIX DAYS
    # =========================================================

    @staticmethod
    def _get_previous_six_days() -> List[datetime.date]:
        """
        Return the six calendar dates immediately preceding
        the current date.

        Example:

        If today is Sunday:

            Monday
            Tuesday
            Wednesday
            Thursday
            Friday
            Saturday

        are returned.

        Returns:
            List[date]:
                Previous six calendar dates.
        """

        today = datetime.now().date()

        return [
            today - timedelta(days=offset)
            for offset in range(6, 0, -1)
        ]

    # =========================================================
    # FILTER HISTORY BY DATE
    # =========================================================

    @staticmethod
    def _questions_from_previous_six_days(
        days: List[datetime.date],
    ) -> List[Question]:
        """
        Filter loaded history to questions created during
        the previous six calendar days.

        Args:
            days:
                Previous six calendar dates.

        Returns:
            List[Question]:
                Questions belonging to those dates.
        """

        valid_dates = set(days)

        history = HistoryManager()

        questions: List[Question] = []

        for question in history.questions:

            created_date = (
                question.created_at.date()
            )

            if created_date in valid_dates:

                questions.append(
                    question
                )

        return questions

    # =========================================================
    # GROUP BY QUESTION TYPE
    # =========================================================

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

    # =========================================================
    # REVISION DISTRIBUTION
    # =========================================================

    @staticmethod
    def _revision_distribution() -> Dict[
        QuestionType,
        int,
    ]:
        """
        Return the required Sunday revision distribution.

        Total:

            10 + 10 + 10 + 10 + 20 + 15 = 75
        """

        return {
            QuestionType.SQUARE: 10,

            QuestionType.CUBE: 10,

            QuestionType.SQUARE_ROOT: 10,

            QuestionType.CUBE_ROOT: 10,

            QuestionType.SIMPLIFICATION: 20,

            QuestionType.NUMBER_SERIES: 15,
        }

    # =========================================================
    # TOTAL REVISION COUNT
    # =========================================================

    @classmethod
    def _total_revision_question_count(
        cls,
    ) -> int:
        """
        Return total number of Sunday revision questions.
        """

        return sum(
            cls._revision_distribution().values()
        )

    # =========================================================
    # OUTPUT FILE NAMES
    # =========================================================

    @staticmethod
    def _revision_question_pdf_name() -> str:
        """
        Return weekly revision question PDF filename.
        """

        return "Weekly_Revision.pdf"

    @staticmethod
    def _revision_answer_pdf_name() -> str:
        """
        Return weekly revision answer PDF filename.
        """

        return "Weekly_Revision_Answers.pdf"

    # =========================================================
    # IDS
    # =========================================================

    @staticmethod
    def _reassign_ids(
        questions: List[Question],
    ) -> None:
        """
        Assign sequential IDs from 1 to 75.
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
    # FINAL HISTORY CLEANUP
    # =========================================================

    def _cleanup_after_revision(
        self,
    ) -> None:
        """
        Clear the completed week's history.

        This method is called only after the Sunday
        revision email has been sent successfully.

        The HistoryManager is cleared both:
        - in memory
        - on disk
        """

        LOGGER.info(
            "Weekly revision completed. "
            "Starting history cleanup."
        )

        self.history.clear()

        LOGGER.info(
            "Weekly revision history cleanup completed."
        )
