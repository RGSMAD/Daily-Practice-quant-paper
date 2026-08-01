"""General helper utilities for the Daily Aptitude Generator."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, List, TypeVar

T = TypeVar("T")


def ensure_directory(path: str | Path) -> Path:
    """Create a directory if it does not already exist.

    Args:
        path:
            Directory path.

    Returns:
        Path:
            Created directory path.
    """
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def ensure_parent_directory(file_path: str | Path) -> Path:
    """Create the parent directory for a file.

    Args:
        file_path:
            File path.

    Returns:
        Path:
            File path as a Path object.
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_current_timestamp() -> str:
    """Return the current timestamp.

    Returns:
        str:
            Timestamp formatted as YYYYMMDD_HHMMSS.
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_current_date() -> str:
    """Return today's date.

    Returns:
        str:
            Date formatted as YYYY-MM-DD.
    """
    return datetime.now().strftime("%Y-%m-%d")


def get_display_date() -> str:
    """Return today's date for display.

    Returns:
        str:
            Date formatted as DD Month YYYY.
    """
    return datetime.now().strftime("%d %B %Y")


def build_output_filename(
    prefix: str,
    extension: str = "pdf",
) -> str:
    """Generate a timestamp-based filename.

    Args:
        prefix:
            Filename prefix.

        extension:
            File extension without the leading dot.

    Returns:
        str:
            Generated filename.
    """
    timestamp = get_current_timestamp()
    return f"{prefix}_{timestamp}.{extension}"


def chunk_list(
    items: List[T],
    chunk_size: int,
) -> List[List[T]]:
    """Split a list into smaller chunks.

    Args:
        items:
            Source list.

        chunk_size:
            Maximum size of each chunk.

    Returns:
        List[List[T]]:
            List of chunks.

    Raises:
        ValueError:
            If chunk_size is less than one.
    """
    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than zero."
        )

    return [
        items[index:index + chunk_size]
        for index in range(0, len(items), chunk_size)
    ]


def flatten(
    nested: Iterable[Iterable[T]],
) -> List[T]:
    """Flatten a nested iterable.

    Args:
        nested:
            Nested iterable.

    Returns:
        List[T]:
            Flattened list.
    """
    return [
        item
        for group in nested
        for item in group
    ]


def unique_preserve_order(
    items: Iterable[T],
) -> List[T]:
    """Remove duplicates while preserving order.

    Args:
        items:
            Input iterable.

    Returns:
        List[T]:
            Unique values in original order.
    """
    seen = set()
    unique_items: List[T] = []

    for item in items:
        if item not in seen:
            seen.add(item)
            unique_items.append(item)

    return unique_items


def safe_int(
    value: object,
    default: int = 0,
) -> int:
    """Safely convert a value to an integer.

    Args:
        value:
            Value to convert.

        default:
            Default value returned upon failure.

    Returns:
        int:
            Converted integer or default value.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def file_exists(path: str | Path) -> bool:
    """Check whether a file exists.

    Args:
        path:
            File path.

    Returns:
        bool:
            True if the file exists.
    """
    return Path(path).is_file()


def directory_exists(path: str | Path) -> bool:
    """Check whether a directory exists.

    Args:
        path:
            Directory path.

    Returns:
        bool:
            True if the directory exists.
    """
    return Path(path).is_dir()