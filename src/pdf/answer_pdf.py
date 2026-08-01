"""
answer_pdf.py

Generates the daily aptitude answer key PDF.
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

        self.margin = (
            settings.pdf.margin
        )


    def generate(
        self,
        answers: List[Answer],
        output_path: Path,
    ) -> Path:
        """
        Generate answer key PDF.

        Args:
            answers:
                List of answer objects.

            output_path:
                PDF output location.

        Returns:
            Path:
                Generated PDF path.
        """

        LOGGER.info(
            "Generating answer PDF."
        )


        pdf = canvas.Canvas(
            str(output_path),
            pagesize=A4,
        )


        pdf.setTitle(
            settings.pdf.answer_pdf_name
        )

        pdf.setAuthor(
            settings.pdf.author
        )


        self._draw_header(
            pdf
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
                    pdf
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



    def _draw_header(
        self,
        pdf: canvas.Canvas,
    ) -> None:
        """
        Draw answer PDF header.

        Args:
            pdf:
                ReportLab canvas object.
        """

        pdf.setFont(
            settings.pdf.font_bold,
            settings.pdf.heading_size,
        )


        pdf.drawString(
            self.margin,
            self.page_height - self.margin,
            "Daily Aptitude Answer Key",
        )



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