"""Date parsing utilities for Indian date formats.

This module provides functions to parse dates commonly found in Indian
credit card statements, handling various formats and edge cases.
"""

import re
from datetime import datetime
from typing import Optional

from dateutil import parser as dateutil_parser

from .exceptions import ValidationError

# Common Indian date formats
INDIAN_DATE_FORMATS = [
    "%d-%m-%Y",  # 25-12-2023
    "%d/%m/%Y",  # 25/12/2023
    "%d.%m.%Y",  # 25.12.2023
    "%d %b %Y",  # 25 Dec 2023
    "%d %B %Y",  # 25 December 2023
    "%d-%b-%Y",  # 25-Dec-2023
    "%d/%b/%Y",  # 25/Dec/2023
    "%d-%B-%Y",  # 25-December-2023
    "%d/%B/%Y",  # 25/December/2023
    "%d-%m-%y",  # 25-12-23
    "%d/%m/%y",  # 25/12/23
    "%d.%m.%y",  # 25.12.23
    "%d %b %y",  # 25 Dec 23
    "%d %B %y",  # 25 December 23
    "%b %d, %Y",  # Dec 25, 2023
    "%B %d, %Y",  # December 25, 2023
    "%Y-%m-%d",  # 2023-12-25 (ISO format)
]

# Month name mappings (abbreviated and full)
MONTH_NAMES = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def normalize_date_string(date_str: str) -> str:
    """Normalize date string by cleaning up common issues.

    Args:
        date_str: Raw date string

    Returns:
        Cleaned date string
    """
    # Remove extra whitespace
    date_str = " ".join(date_str.split())

    # Remove common prefixes
    date_str = re.sub(r"^(date:|dated:)\s*", "", date_str, flags=re.IGNORECASE)

    # Handle multiple separators (e.g., "25--12--2023" -> "25-12-2023")
    date_str = re.sub(r"[-/\.]{2,}", "-", date_str)

    return date_str.strip()


def parse_date(
    date_str: str,
    default_year: Optional[int] = None,
    fuzzy: bool = True,
) -> Optional[datetime]:
    """Parse a date string in various Indian formats.

    Args:
        date_str: Date string to parse
        default_year: Year to use if not specified in the date string
        fuzzy: If True, allow fuzzy parsing (extract date from text)

    Returns:
        Parsed datetime object or None if parsing fails

    Raises:
        ValidationError: If date string is invalid and cannot be parsed
    """
    if not date_str or not isinstance(date_str, str):
        return None

    # Normalize the input
    date_str = normalize_date_string(date_str)

    # Try each format explicitly
    for fmt in INDIAN_DATE_FORMATS:
        try:
            parsed = datetime.strptime(date_str, fmt)
            # Handle 2-digit years (assume 2000+ for years < 50, 1900+ otherwise)
            if parsed.year < 100:
                if parsed.year < 50:
                    parsed = parsed.replace(year=parsed.year + 2000)
                else:
                    parsed = parsed.replace(year=parsed.year + 1900)
            return parsed
        except ValueError:
            continue

    # Try dateutil parser for more flexible parsing
    if fuzzy:
        try:
            parsed = dateutil_parser.parse(date_str, fuzzy=True, dayfirst=True)
            if default_year and parsed.year == datetime.now().year:
                # If no year was found and default is provided, use it
                parsed = parsed.replace(year=default_year)
            return parsed
        except (ValueError, TypeError):
            pass

    return None


def parse_date_strict(date_str: str) -> datetime:
    """Parse a date string strictly, raising an error if parsing fails.

    Args:
        date_str: Date string to parse

    Returns:
        Parsed datetime object

    Raises:
        ValidationError: If date string cannot be parsed
    """
    result = parse_date(date_str, fuzzy=False)
    if result is None:
        raise ValidationError(
            f"Invalid date format: '{date_str}'",
            details={"input": date_str, "supported_formats": INDIAN_DATE_FORMATS},
        )
    return result


def extract_dates_from_text(text: str) -> list[datetime]:
    """Extract all dates from a text string.

    Args:
        text: Text containing dates

    Returns:
        List of parsed datetime objects found in the text
    """
    dates = []

    # Pattern for common date formats
    date_patterns = [
        r"\b\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}\b",  # 25-12-2023, 25/12/23
        r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{2,4}\b",  # 25 Dec 2023
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b",  # Dec 25, 2023
    ]

    for pattern in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            date_str = match.group(0)
            parsed = parse_date(date_str, fuzzy=False)
            if parsed:
                dates.append(parsed)

    return dates


def format_date_indian(dt: datetime, format_type: str = "long") -> str:
    """Format a datetime object in Indian format.

    Args:
        dt: Datetime object to format
        format_type: Format type - "short" (DD-MM-YYYY), "long" (DD Month YYYY)

    Returns:
        Formatted date string
    """
    if format_type == "short":
        return dt.strftime("%d-%m-%Y")
    elif format_type == "long":
        return dt.strftime("%d %B %Y")
    else:
        return dt.strftime("%d-%m-%Y")


def parse_date_range(
    start_str: str,
    end_str: str,
) -> tuple[datetime, datetime]:
    """Parse a date range from two date strings.

    Args:
        start_str: Start date string
        end_str: End date string

    Returns:
        Tuple of (start_date, end_date)

    Raises:
        ValidationError: If either date cannot be parsed or if end < start
    """
    start_date = parse_date_strict(start_str)
    end_date = parse_date_strict(end_str)

    if end_date < start_date:
        raise ValidationError(
            "End date must be after start date",
            details={"start": start_str, "end": end_str},
        )

    return start_date, end_date


def is_valid_date_string(date_str: str) -> bool:
    """Check if a string can be parsed as a valid date.

    Args:
        date_str: Date string to validate

    Returns:
        True if the string can be parsed as a date, False otherwise
    """
    return parse_date(date_str, fuzzy=False) is not None


def get_financial_year(dt: datetime) -> str:
    """Get the financial year for a given date (April to March).

    Args:
        dt: Date to get financial year for

    Returns:
        Financial year string (e.g., "2023-24")
    """
    if dt.month >= 4:
        # April onwards belongs to current-next year
        return f"{dt.year}-{str(dt.year + 1)[-2:]}"
    else:
        # Jan-Mar belongs to previous-current year
        return f"{dt.year - 1}-{str(dt.year)[-2:]}"
