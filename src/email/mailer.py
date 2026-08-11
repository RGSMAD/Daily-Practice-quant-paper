
"""
mailer.py

Email service for sending generated aptitude PDFs.
"""

from __future__ import annotations

import mimetypes
import os
import smtplib

from email.message import EmailMessage
from pathlib import Path
from typing import Iterable

from src.config import settings
from src.utils.logger import get_logger
from src.utils.validator import validate_file_exists


LOGGER = get_logger(__name__)


class EmailSender:
    """
    Handles email delivery of generated PDF files.
    """

    def __init__(self) -> None:
        """
        Initialize email configuration.
        """

        self.smtp_server = (
            settings.email.smtp_server
        )

        self.smtp_port = (
            settings.email.smtp_port
        )

        self.use_tls = (
            settings.email.use_tls
        )

        self.username = os.getenv(
            settings.email.sender_env
        )

        self.password = os.getenv(
            settings.email.password_env
        )

        self.sender = self.username

        self.recipient = os.getenv(
            settings.email.receiver_env
        )

    # =========================================================
    # SEND EMAIL
    # =========================================================

    def send(
        self,
        attachments: Iterable[str | Path],
        subject: str | None = None,
        body: str | None = None,
    ) -> None:
        """
        Send aptitude PDFs through email.

        Args:
            attachments:
                PDF files to attach.

            subject:
                Optional email subject.
                Falls back to settings.email.subject
                when not provided.

            body:
                Optional email body.
                Falls back to settings.email.body
                when not provided.

        Raises:
            ValueError:
                If email configuration is missing.
        """

        self._validate_email_configuration()

        message = EmailMessage()

        message["Subject"] = (
            subject
            if subject is not None
            else settings.email.subject
        )

        message["From"] = (
            self.sender
        )

        message["To"] = (
            self.recipient
        )

        message.set_content(
            body
            if body is not None
            else settings.email.body
        )

        for attachment in attachments:

            self._attach_file(
                message,
                Path(attachment),
            )

        try:

            with smtplib.SMTP(
                self.smtp_server,
                self.smtp_port,
            ) as smtp:

                if self.use_tls:

                    smtp.starttls()

                smtp.login(
                    self.username,
                    self.password,
                )

                smtp.send_message(
                    message
                )

            LOGGER.info(
                "Email sent successfully to %s",
                self.recipient,
            )

        except smtplib.SMTPException:

            LOGGER.exception(
                "Failed to send email."
            )

            raise

    # =========================================================
    # VALIDATE EMAIL CONFIGURATION
    # =========================================================

    def _validate_email_configuration(
        self,
    ) -> None:
        """
        Validate email credentials.

        Raises:
            ValueError:
                If required environment variables
                are missing.
        """

        if not self.username:

            raise ValueError(
                "Sender email is not configured."
            )

        if not self.password:

            raise ValueError(
                "Email password is not configured."
            )

        if not self.recipient:

            raise ValueError(
                "Receiver email is not configured."
            )

    # =========================================================
    # ATTACH FILE
    # =========================================================

    @staticmethod
    def _attach_file(
        message: EmailMessage,
        file_path: Path,
    ) -> None:
        """
        Attach a file to an email.

        Args:
            message:
                Email message object.

            file_path:
                Attachment path.
        """

        validate_file_exists(
            file_path
        )

        mime_type, _ = mimetypes.guess_type(
            str(file_path)
        )

        if mime_type:

            main_type, sub_type = (
                mime_type.split(
                    "/",
                    maxsplit=1,
                )
            )

        else:

            main_type = (
                "application"
            )

            sub_type = (
                "octet-stream"
            )

        with file_path.open(
            "rb",
        ) as file:

            message.add_attachment(
                file.read(),
                maintype=main_type,
                subtype=sub_type,
                filename=file_path.name,
            )

