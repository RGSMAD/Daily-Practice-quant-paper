"""
main.py

Application entry point for the Daily Aptitude Generator.

Responsible for starting the daily workflow:
- Generate aptitude questions
- Create PDFs
- Send email notification
"""

from __future__ import annotations

import sys

from src.generator import AptitudeGenerator
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


def main() -> int:
    """
    Execute the daily aptitude generation workflow.

    Returns:
        int:
            Process exit status.
            0 indicates success.
            Non-zero indicates failure.
    """

    try:

        LOGGER.info(
            "Daily Aptitude Generator started."
        )


        generator = (
            AptitudeGenerator()
        )


        generator.generate_and_send()


        LOGGER.info(
            "Daily Aptitude Generator completed successfully."
        )


        return 0


    except Exception:

        LOGGER.exception(
            "Daily Aptitude Generator failed."
        )


        return 1



if __name__ == "__main__":

    sys.exit(
        main()
    )