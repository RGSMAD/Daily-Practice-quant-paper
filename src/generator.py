
"""
generator.py

Main orchestration service for the
Daily Aptitude Generator.

Responsible for:

- Generating daily aptitude questions
- Checking question history for duplicates
- Saving generated questions to history
- Creating PDFs
- Sending email notifications

Weekly revision generation is handled separately
by src/new_revision.py.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from src.config import settings
from src.email.mailer import EmailSender

from src.generators.square_generator import SquareGenerator
from src.generators.cube_generator import CubeGenerator
from src.generators.square_root_generator import SquareRootGenerator
from src.generators.cube_root_generator import CubeRootGenerator
from src.generators.simplification_generator import SimplificationGenerator
from src.generators.series_generator import SeriesGenerator

from src.models.answer import Answer
from src.models.question import Question

from src.pdf.answer_pdf import AnswerPDFGenerator
from src.pdf.question_pdf import QuestionPDFGenerator

from src.utils.history import HistoryManager
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


class AptitudeGenerator:
    """
    Coordinates the normal daily aptitude generation workflow.

    This class is used for the regular daily paper.

    It does NOT perform weekly revision or history cleanup.
    """

    def __init__(self) -> None:
        """
        Initialize daily aptitude generation services.
        """

        self.history = HistoryManager()

        self.question_pdf = QuestionPDFGenerator()

        self.answer_pdf = AnswerPDFGenerator()

        self.email_sender = EmailSender()

    # =========================================================
    # MAIN GENERATION FLOW
    # =========================================================

    def generate(
        self,
    ) -> Tuple[Path, Path]:
        """
        Generate the daily aptitude paper.

        Workflow:

        1. Generate questions category-wise.
        2. Reject questions already present in history.
        3. Add today's questions to history.
        4. Save history.
        5. Generate question PDF.
        6. Generate answer PDF.

        Returns:
            Tuple[Path, Path]:
                Question PDF path and answer PDF path.
        """

        LOGGER.info(
            "Starting daily aptitude generation."
        )

        questions = (
            self._generate_questions()
        )

        if len(questions) != self._total_question_count():

            raise RuntimeError(
                "Daily question generation completed "
                "with an unexpected question count: "
                f"{len(questions)}"
            )

        # -----------------------------------------------------
        # Save today's questions.
        #
        # IMPORTANT:
        # No cleanup is performed here.
        #
        # The complete six-day history must remain available
        # for Sunday's weekly revision.
        # -----------------------------------------------------

        self.history.add_questions(
            questions
        )

        self.history.save()

        LOGGER.info(
            "Today's %s questions saved to history.",
            len(questions),
        )

        # -----------------------------------------------------
        # Create answers
        # -----------------------------------------------------

        answers = (
            self._create_answers(
                questions
            )
        )

        # -----------------------------------------------------
        # Output directory
        # -----------------------------------------------------

        output_dir = (
            settings.paths.output_dir
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # -----------------------------------------------------
        # Output paths
        # -----------------------------------------------------

        question_pdf_path = (
            output_dir
            / settings.pdf.question_pdf_name
        )

        answer_pdf_path = (
            output_dir
            / settings.pdf.answer_pdf_name
        )

        # -----------------------------------------------------
        # Generate question PDF
        # -----------------------------------------------------

        self.question_pdf.generate(
            questions,
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
            "Daily PDF generation completed."
        )

        return (
            question_pdf_path,
            answer_pdf_path,
        )

    # =========================================================
    # EMAIL
    # =========================================================

    def generate_and_send(
        self,
    ) -> None:
        """
        Generate the daily paper and send it by email.
        """

        question_pdf, answer_pdf = (
            self.generate()
        )

        self.email_sender.send(
            [
                question_pdf,
                answer_pdf,
            ]
        )

        LOGGER.info(
            "Daily aptitude email completed."
        )

    # =========================================================
    # QUESTION GENERATION
    # =========================================================

    def _generate_questions(
        self,
    ) -> List[Question]:
        """
        Generate questions category-wise.

        Each category is generated independently.

        Duplicate questions are rejected against:

        1. Existing history.
        2. Questions already selected for today.

        When a duplicate is found, another question from
        the same generator is requested.

        Returns:
            List[Question]:
                Complete daily question set.
        """

        generator_config = [

            (
                SquareGenerator(),
                settings.questions.square_questions,
            ),

            (
                CubeGenerator(),
                settings.questions.cube_questions,
            ),

            (
                SquareRootGenerator(),
                settings.questions.square_root_questions,
            ),

            (
                CubeRootGenerator(),
                settings.questions.cube_root_questions,
            ),

            (
                SimplificationGenerator(),
                settings.questions.simplification_questions,
            ),

            (
                SeriesGenerator(),
                settings.questions.series_questions,
            ),
        ]

        selected_questions: List[Question] = []

        for generator, required_count in generator_config:

            category_questions: List[
                Question
            ] = []

            attempts = 0

            while len(category_questions) < required_count:

                attempts += 1

                if attempts > 100:

                    raise RuntimeError(
                        f"Unable to generate enough "
                        f"unique questions for "
                        f"{generator.__class__.__name__}. "
                        f"Required: {required_count}, "
                        f"Generated: "
                        f"{len(category_questions)}."
                    )

                generated = (
                    generator.generate()
                )

                for question in generated:

                    if (
                        len(category_questions)
                        >= required_count
                    ):
                        break

                    if self._is_duplicate(
                        question,
                        selected_questions
                        + category_questions,
                    ):

                        LOGGER.info(
                            "Duplicate rejected: %s",
                            question.question,
                        )

                        continue

                    category_questions.append(
                        question
                    )

            LOGGER.info(
                "%s finalized %s questions.",
                generator.__class__.__name__,
                len(category_questions),
            )

            selected_questions.extend(
                category_questions
            )

        # -----------------------------------------------------
        # Reassign IDs after all categories are combined.
        # -----------------------------------------------------

        self._reassign_ids(
            selected_questions
        )

        LOGGER.info(
            "Generated %s unique daily questions.",
            len(selected_questions),
        )

        return selected_questions

    # =========================================================
    # QUESTION COUNT
    # =========================================================

    @staticmethod
    def _total_question_count() -> int:
        """
        Return the configured total number of daily questions.
        """

        return (
            settings.questions.square_questions
            + settings.questions.cube_questions
            + settings.questions.square_root_questions
            + settings.questions.cube_root_questions
            + settings.questions.simplification_questions
            + settings.questions.series_questions
        )

    # =========================================================
    # DUPLICATE CHECK
    # =========================================================

    def _is_duplicate(
        self,
        question: Question,
        current_questions: List[Question],
    ) -> bool:
        """
        Check whether a question is already present
        in history or today's generated set.
        """

        if self.history.is_duplicate(
            question
        ):

            return True

        return any(
            existing.fingerprint
            == question.fingerprint
            for existing in current_questions
        )

    # =========================================================
    # IDS
    # =========================================================

    @staticmethod
    def _reassign_ids(
        questions: List[Question],
    ) -> None:
        """
        Assign sequential IDs to the complete
        daily question set.
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
        the generated questions.
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
