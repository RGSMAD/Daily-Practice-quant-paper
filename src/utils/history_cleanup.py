"""
history_cleanup.py

Runs periodic cleanup of the question history.
"""

from src.utils.history import (
    HistoryManager,
)


def main() -> None:
    history = HistoryManager()
    history.cleanup()


if __name__ == "__main__":
    main()