
"""
main.py

Application entry point for the Daily Aptitude Generator.

Responsible for selecting and starting the appropriate workflow:

- Monday-Saturday:
    Generate fresh daily aptitude questions,
    create PDFs, save questions to history,
    and send email notification.

- Sunday:
    Generate a weekly revision paper using questions
    from the previous six days, create PDFs,
    send the revision email, and clean the
    completed week's history.
"""

from __future__ import annotations

import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from src.config import settings
from src.generator import AptitudeGenerator
from src.new_revision import RevisionGenerator
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


# ============================================================
# WORKFLOW SELECTION
# ============================================================

def _is_revision_day() -> bool:
    """
    Determine whether today is the configured revision day.

    The application timezone is taken from config.yaml.

    Returns:
        bool:
            True when today matches the configured revision day.
            False otherwise.
    """

    timezone = ZoneInfo(
        settings.app.timezone
    )

    today = datetime.now(
        timezone
    )

    current_day = today.strftime(
        "%A"
    )

    revision_day = (
        settings.revision.revision_day
    )

    return (
        current_day.lower()
        == revision_day.lower()
    )


# ============================================================
# MAIN APPLICATION
# ============================================================

def main() -> int:
    """
    Execute the appropriate daily workflow.

    Monday-Saturday runs the normal question generation
    workflow.

    The configured revision day runs the weekly revision
    workflow.

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


        if _is_revision_day():

            LOGGER.info(
                "Today is the configured revision day: %s",
                settings.revision.revision_day,
            )


            revision_generator = (
                RevisionGenerator()
            )


            revision_generator.generate_and_send()


            LOGGER.info(
                "Weekly revision workflow completed successfully."
            )


        else:

            LOGGER.info(
                "Today is a normal daily practice day."
            )


            generator = (
                AptitudeGenerator()
            )


            generator.generate_and_send()


            LOGGER.info(
                "Daily aptitude workflow completed successfully."
            )


        LOGGER.info(
            "Daily Aptitude Generator completed successfully."
        )


        return 0


    except Exception:

        LOGGER.exception(
            "Daily Aptitude Generator failed."
        )


        return 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    sys.exit(
        main()
    )
