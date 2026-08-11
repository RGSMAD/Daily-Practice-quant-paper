
"""
new_revision.py

Weekly revision workflow for the
Daily Aptitude Generator.

Sunday workflow:

    Monday - Saturday
        |
        | Questions are generated normally
        | Questions are stored in active history
        v
    active.json
        |
        | Sunday
        v
    Read previous six days
        |
        +--> 10 Squares
        +--> 10 Cubes
        +--> 10 Square Roots
        +--> 10 Cube Roots
        +--> 20 Simplification
        +--> 15 Number Series
        |
        v
    75 revision questions
        |
        +--> Question PDF
        +--> Answer PDF
        |
        v
    Send email
        |
        v
    Successful completion
        |
        v
    Clear active history

Important:

    Sunday does NOT generate new aptitude questions.

    Every Sunday revision question must come from
    the questions generated during the previous six
    calendar days.

    History is cleared only after the complete
    revision workflow succeeds.
"""

from __future__ import annotations

import random

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

from src.config import settings
from src.models.answer import Answer
from src.models.enums import QuestionType
from src.models.question import Question
from src.pdf.answer_pdf import AnswerPDFGenerator
from src.pdf.question_pdf import QuestionPDFGenerator
from src.utils.history import HistoryManager
from src.utils.logger import get_logger

# IMPORTANT:
# Use the actual location of mailer.py in this project.
from src.mailer import EmailSender


LOGGER = get_logger(__name__)


class WeeklyRevisionGenerator:
    """
    Coordinates the complete Sunday weekly
    revision workflow.

    Sunday does not generate fresh questions.

    Instead, it selects questions from the
    previous six days of generated history.
    """

    # =========================================================
    # REVISION CONFIGURATION
    # =========================================================

    REVISION_TITLE = "Weekly Aptitude Revision"

    REVISION_ANSWER_TITLE = (
        "Weekly Aptitude Revision Answer Key"
    )

    REVISION_EMAIL_SUBJECT = (
        "Weekly Aptitude Revision"
    )

    REVISION_EMAIL_BODY = (
        "Hello,\n\n"
        "Please find this week's aptitude "
        "revision paper attached.\n\n"
        "Happy Learning!"
    )

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

        self.email_sender = EmailSender()

    # =========================================================
    # MAIN REVISION WORKFLOW
    # =========================================================

    def generate(
        self,
    ) -> Tuple[Path, Path]:
        """
        Generate the Sunday weekly revision PDFs.

        This method:

            1. Reads the previous six days of history.
            2. Selects exactly 75 questions.
            3. Creates the question PDF.
            4. Creates the answer PDF.

        History is NOT cleared here.

        Returns:
            Tuple[Path, Path]:
                Question PDF path and answer PDF path.

        Raises:
            RuntimeError:
                If insufficient historical questions
                are available.
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

        output_directory = (
            settings.paths.output_dir
        )

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        question_pdf_path = (
            output_directory
            / self._revision_question_pdf_name()
        )

        answer_pdf_path = (
            output_directory
            / self._revision_answer_pdf_name()
        )

        # -----------------------------------------------------
        # Generate question PDF
        # -----------------------------------------------------

        self.question_pdf.generate(
            revision_questions,
            question_pdf_path,
        )

        LOGGER.info(
            "Weekly revision question PDF generated: %s",
            question_pdf_path,
        )

        # -----------------------------------------------------
        # Generate answer PDF
        # -----------------------------------------------------

        self.answer_pdf.generate(
            answers,
            answer_pdf_path,
        )

        LOGGER.info(
            "Weekly revision answer PDF generated: %s",
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
    # GENERATE AND SEND
    # =========================================================

    def generate_and_send(
        self,
    ) -> None:
        """
        Generate and send the Sunday revision paper.

        History is cleared ONLY after:

            1. Revision questions are successfully selected.
            2. Question PDF is successfully generated.
            3. Answer PDF is successfully generated.
            4. Email is successfully sent.

        If any step fails, the active history remains
        untouched.
        """

        LOGGER.info(
            "Starting complete Sunday revision workflow."
        )

        question_pdf, answer_pdf = (
            self.generate()
        )

        # -----------------------------------------------------
        # Send both PDFs
        # -----------------------------------------------------

        self.email_sender.send(
            [
                question_pdf,
                answer_pdf,
            ]
        )

        LOGGER.info(
            "Weekly revision email sent successfully."
        )

        # -----------------------------------------------------
        # Cleanup only after the complete workflow
        # succeeds.
        # -----------------------------------------------------

        self._cleanup_after_revision()

        LOGGER.info(
            "Sunday weekly revision workflow completed "
            "successfully."
        )

    # =========================================================
    # REVISION QUESTION SELECTION
    # =========================================================

    def _select_revision_questions(
        self,
    ) -> List[Question]:
        """
        Select revision questions from the previous
        six calendar days.

        Required distribution:

            Squares             : 10
            Cubes               : 10
            Square Roots        : 10
            Cube Roots          : 10
            Simplification      : 20
            Number Series       : 15

            Total               : 75

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

        # -----------------------------------------------------
        # Select the configured number for each topic.
        # -----------------------------------------------------

        for (
            question_type,
            required_count,
        ) in required_counts.items():

            available_questions = (
                questions_by_type.get(
                    question_type,
                    [],
                )
            )

            available_count = len(
                available_questions
            )

            if available_count < required_count:

                raise RuntimeError(
                    "Insufficient historical questions "
                    f"for topic '{question_type.value}'. "
                    f"Required: {required_count}, "
                    f"available: {available_count}."
                )

            selected = random.sample(
                available_questions,
                required_count,
            )

            selected_questions.extend(
                selected
            )

            LOGGER.info(
                "Selected %s questions for topic '%s'.",
                required_count,
                question_type.value,
            )

        # -----------------------------------------------------
        # Shuffle the complete paper.
        #
        # This prevents the revision paper from appearing
        # as six separate generator sections.
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
        Return the six calendar dates immediately
        preceding today.

        On Sunday this produces:

            Monday
            Tuesday
            Wednesday
            Thursday
            Friday
            Saturday

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

    def _questions_from_previous_six_days(
        self,
        days: List[datetime.date],
    ) -> List[Question]:
        """
        Filter active history to questions created
        during the previous six calendar days.

        Args:
            days:
                Previous six calendar dates.

        Returns:
            List[Question]:
                Historical questions belonging to
                those dates.
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

        Returns:
            Dictionary mapping QuestionType to
            matching historical questions.
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
        Return the exact Sunday revision distribution.

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
        Return the total number of Sunday
        revision questions.
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
        Return Sunday revision question PDF filename.
        """

        return "Weekly_Revision.pdf"

    @staticmethod
    def _revision_answer_pdf_name() -> str:
        """
        Return Sunday revision answer PDF filename.
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

        The original historical question IDs are not
        retained in the Sunday revision paper.
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
        Create Answer objects for the revision paper.
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

    # =========================================================
    # FINAL HISTORY CLEANUP
    # =========================================================

    def _cleanup_after_revision(
        self,
    ) -> None:
        """
        Clear the completed week's active history.

        This method is called only after:

            - Question PDF generated
            - Answer PDF generated
            - Email successfully sent

        The active history is cleared both:

            1. From memory
            2. From active.json
        """

        LOGGER.info(
            "Weekly revision completed successfully. "
            "Starting history cleanup."
        )

        self.history.cleanup_after_review()

        LOGGER.info(
            "Weekly revision history cleanup completed."
        )
