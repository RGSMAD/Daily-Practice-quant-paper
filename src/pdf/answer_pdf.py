
"""
answer_pdf.py

Generates aptitude answer key PDFs.

The same generator is used for:
- Daily aptitude practice
- Weekly revision practice
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from src.config import settings
from src.models.answer import Answer
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


class AnswerPDFGenerator:
    """
    Generates PDF containing aptitude answers.
    """

    def __init__(self) -> None:
        """
        Initialize PDF configuration.
        """

        self.page_width, self.page_height = A4

        self.margin = settings.pdf.margin

    # =========================================================
    # MAIN PDF GENERATOR
    # =========================================================

    def generate(
        self,
        answers: List[Answer],
        output_path: Path,
        title: str | None = None,
    ) -> Path:
        """
        Generate answer key PDF.

        Args:
            answers:
                List of answer objects.

            output_path:
                Destination PDF path.

            title:
                Optional PDF/header title.

                If omitted, the configured daily
                answer PDF title is used.

        Returns:
            Path:
                Generated PDF path.
        """

        LOGGER.info(
            "Generating answer PDF: %s",
            output_path,
        )

        pdf = canvas.Canvas(
            str(output_path),
            pagesize=A4,
        )

        document_title = (
            title
            if title is not None
            else "Daily Aptitude Answer Key"
        )

        pdf.setTitle(
            document_title
        )

        pdf.setAuthor(
            settings.pdf.author
        )

        self._draw_header(
            pdf,
            document_title,
        )

        y_position = (
            self.page_height
            - self.margin * 2
        )

        for index, answer in enumerate(
            answers,
            start=1,
        ):

            if y_position < 80:

                self._add_page_number(
                    pdf
                )

                pdf.showPage()

                self._draw_header(
                    pdf,
                    document_title,
                )

                y_position = (
                    self.page_height
                    - self.margin * 2
                )

            text = (
                f"{index}. "
                f"{answer.answer}"
            )

            pdf.setFont(
                settings.pdf.font_name,
                settings.pdf.font_size,
            )

            pdf.drawString(
                self.margin,
                y_position,
                text,
            )

            y_position -= (
                settings.pdf.line_spacing
            )

        self._add_page_number(
            pdf
        )

        pdf.save()

        LOGGER.info(
            "Answer PDF created: %s",
            output_path,
        )

        return output_path

    # =========================================================
    # HEADER
    # =========================================================

    def _draw_header(
        self,
        pdf: canvas.Canvas,
        title: str,
    ) -> None:
        """
        Draw answer PDF header.

        Args:
            pdf:
                ReportLab canvas object.

            title:
                Header title.
        """

        pdf.setFont(
            settings.pdf.font_bold,
            settings.pdf.heading_size,
        )

        pdf.drawString(
            self.margin,
            self.page_height - self.margin,
            title,
        )

    # =========================================================
    # PAGE NUMBER
    # =========================================================

    def _add_page_number(
        self,
        pdf: canvas.Canvas,
    ) -> None:
        """
        Add page number.

        Args:
            pdf:
                ReportLab canvas object.
        """

        if not settings.pdf.show_page_numbers:

            return

        page_number = (
            pdf.getPageNumber()
        )

        pdf.setFont(
            settings.pdf.font_name,
            9,
        )

        pdf.drawRightString(
            self.page_width - self.margin,
            25,
            f"Page {page_number}",
        )
