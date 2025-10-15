"""Currency parsing utilities for Indian Rupee amounts.

This module provides functions to parse monetary amounts in Indian formats,
handling rupee symbols, lakhs, crores, and various formatting conventions.
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Optional, Union

from .exceptions import ValidationError

# Currency symbols and prefixes
CURRENCY_SYMBOLS = ["₹", "Rs", "Rs.", "INR", "rs"]

# Regex patterns for currency amounts
AMOUNT_PATTERNS = [
    # With currency symbol: ₹1,23,456.78 or Rs. 1,23,456.78
    r"(?:[₹]|Rs\.?|INR)\s*(-?\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)",
    # Without currency symbol but with lakhs/crores format: 1,23,456.78
    r"(-?\d{1,3}(?:,\d{2,3})+(?:\.\d{2})?)",
    # Simple format: 12345.67 or 12345
    r"(-?\d+(?:\.\d{2})?)",
]

# Words for large numbers
LAKH_PATTERN = r"(\d+(?:\.\d+)?)\s*(?:lakh|lac)s?"
CRORE_PATTERN = r"(\d+(?:\.\d+)?)\s*(?:crore|cr)s?"


def normalize_amount_string(amount_str: str) -> str:
    """Normalize amount string by cleaning up common issues.

    Args:
        amount_str: Raw amount string

    Returns:
        Cleaned amount string
    """
    # Remove extra whitespace
    amount_str = " ".join(amount_str.split())

    # Handle parentheses for negative amounts: (1234.56) -> -1234.56
    if amount_str.startswith("(") and amount_str.endswith(")"):
        amount_str = "-" + amount_str[1:-1]

    # Remove common text prefixes
    amount_str = re.sub(
        r"^(amount:|total:|balance:|rs\.?|inr)\s*",
        "",
        amount_str,
        flags=re.IGNORECASE,
    )

    return amount_str.strip()


def remove_currency_symbols(amount_str: str) -> str:
    """Remove currency symbols from amount string.

    Args:
        amount_str: Amount string with currency symbols

    Returns:
        Amount string without currency symbols
    """
    for symbol in CURRENCY_SYMBOLS:
        amount_str = amount_str.replace(symbol, "")
    return amount_str.strip()


def parse_lakh_crore(amount_str: str) -> Optional[Decimal]:
    """Parse amounts specified in lakhs or crores.

    Args:
        amount_str: Amount string containing lakh/crore (e.g., "5.5 lakhs")

    Returns:
        Decimal value or None if not in lakh/crore format
    """
    amount_str_lower = amount_str.lower()

    # Check for crores (1 crore = 10,000,000)
    crore_match = re.search(CRORE_PATTERN, amount_str_lower, re.IGNORECASE)
    if crore_match:
        try:
            value = Decimal(crore_match.group(1))
            return value * Decimal("10000000")
        except InvalidOperation:
            return None

    # Check for lakhs (1 lakh = 100,000)
    lakh_match = re.search(LAKH_PATTERN, amount_str_lower, re.IGNORECASE)
    if lakh_match:
        try:
            value = Decimal(lakh_match.group(1))
            return value * Decimal("100000")
        except InvalidOperation:
            return None

    return None


def parse_currency(
    amount_str: str,
    default_value: Optional[Decimal] = None,
) -> Optional[Decimal]:
    """Parse a currency amount string in Indian format.

    Args:
        amount_str: Amount string to parse (e.g., "₹1,23,456.78", "5.5 lakhs")
        default_value: Value to return if parsing fails

    Returns:
        Decimal value or default_value if parsing fails
    """
    if not amount_str or not isinstance(amount_str, str):
        return default_value

    # Normalize the input
    amount_str = normalize_amount_string(amount_str)

    # Check for lakh/crore notation first
    lakh_crore_value = parse_lakh_crore(amount_str)
    if lakh_crore_value is not None:
        return lakh_crore_value

    # Remove currency symbols
    amount_str = remove_currency_symbols(amount_str)

    # Remove spaces
    amount_str = amount_str.replace(" ", "")

    # Try to extract numeric value
    try:
        # Remove commas (Indian formatting uses them differently than Western)
        amount_str = amount_str.replace(",", "")

        # Handle negative sign
        is_negative = amount_str.startswith("-")
        if is_negative:
            amount_str = amount_str[1:]

        # Convert to Decimal
        value = Decimal(amount_str)

        # Apply negative sign if needed
        if is_negative:
            value = -value

        return value

    except (InvalidOperation, ValueError):
        return default_value


def parse_currency_strict(amount_str: str) -> Decimal:
    """Parse a currency amount strictly, raising an error if parsing fails.

    Args:
        amount_str: Amount string to parse

    Returns:
        Decimal value

    Raises:
        ValidationError: If amount string cannot be parsed
    """
    result = parse_currency(amount_str)
    if result is None:
        raise ValidationError(
            f"Invalid currency format: '{amount_str}'",
            details={"input": amount_str},
        )
    return result


def extract_amounts_from_text(text: str) -> list[Decimal]:
    """Extract all currency amounts from a text string.

    Args:
        text: Text containing amounts

    Returns:
        List of Decimal values found in the text
    """
    amounts = []

    # First check for lakh/crore amounts
    for pattern in [CRORE_PATTERN, LAKH_PATTERN]:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            amount = parse_lakh_crore(match.group(0))
            if amount:
                amounts.append(amount)

    # Then check for regular currency amounts
    for pattern in AMOUNT_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Get the numeric part (group 1 or 0)
            try:
                amount_str = match.group(1) if match.lastindex else match.group(0)
            except IndexError:
                amount_str = match.group(0)

            amount = parse_currency(amount_str)
            if amount and amount not in amounts:
                amounts.append(amount)

    return amounts


def format_currency_indian(
    amount: Union[Decimal, float, int],
    include_symbol: bool = True,
    include_decimals: bool = True,
) -> str:
    """Format an amount in Indian currency format.

    Args:
        amount: Amount to format
        include_symbol: If True, include ₹ symbol
        include_decimals: If True, include decimal places

    Returns:
        Formatted currency string (e.g., "₹1,23,456.78")
    """
    if isinstance(amount, (float, int)):
        amount = Decimal(str(amount))

    # Handle negative amounts
    is_negative = amount < 0
    amount = abs(amount)

    # Split into integer and decimal parts
    if include_decimals:
        amount_str = f"{amount:.2f}"
    else:
        amount_str = str(int(amount))

    parts = amount_str.split(".")
    integer_part = parts[0]
    decimal_part = parts[1] if len(parts) > 1 else None

    # Apply Indian number formatting (groups of 2 after the first 3 digits)
    if len(integer_part) > 3:
        # Last 3 digits
        formatted = integer_part[-3:]
        remaining = integer_part[:-3]

        # Groups of 2 for the rest
        while remaining:
            if len(remaining) > 2:
                formatted = remaining[-2:] + "," + formatted
                remaining = remaining[:-2]
            else:
                formatted = remaining + "," + formatted
                remaining = ""
    else:
        formatted = integer_part

    # Add decimal part if present
    if decimal_part and include_decimals:
        formatted += "." + decimal_part

    # Add negative sign if needed
    if is_negative:
        formatted = "-" + formatted

    # Add currency symbol if requested
    if include_symbol:
        formatted = "₹" + formatted

    return formatted


def format_in_lakhs(amount: Union[Decimal, float, int]) -> str:
    """Format an amount in lakhs.

    Args:
        amount: Amount to format

    Returns:
        Formatted string (e.g., "12.35 lakhs")
    """
    if isinstance(amount, (float, int)):
        amount = Decimal(str(amount))

    lakhs = amount / Decimal("100000")
    return f"{lakhs:.2f} lakhs"


def format_in_crores(amount: Union[Decimal, float, int]) -> str:
    """Format an amount in crores.

    Args:
        amount: Amount to format

    Returns:
        Formatted string (e.g., "1.23 crores")
    """
    if isinstance(amount, (float, int)):
        amount = Decimal(str(amount))

    crores = amount / Decimal("10000000")
    return f"{crores:.2f} crores"


def is_valid_amount(amount_str: str) -> bool:
    """Check if a string can be parsed as a valid currency amount.

    Args:
        amount_str: Amount string to validate

    Returns:
        True if the string can be parsed as an amount, False otherwise
    """
    return parse_currency(amount_str) is not None


def compare_amounts(
    amount1: Union[str, Decimal, float],
    amount2: Union[str, Decimal, float],
    tolerance: Decimal = Decimal("0.01"),
) -> int:
    """Compare two amounts with a tolerance for floating point errors.

    Args:
        amount1: First amount
        amount2: Second amount
        tolerance: Acceptable difference for equality

    Returns:
        -1 if amount1 < amount2, 0 if equal (within tolerance), 1 if amount1 > amount2
    """
    # Parse if strings
    if isinstance(amount1, str):
        amount1 = parse_currency_strict(amount1)
    elif isinstance(amount1, (float, int)):
        amount1 = Decimal(str(amount1))

    if isinstance(amount2, str):
        amount2 = parse_currency_strict(amount2)
    elif isinstance(amount2, (float, int)):
        amount2 = Decimal(str(amount2))

    diff = amount1 - amount2

    if abs(diff) <= tolerance:
        return 0
    elif diff < 0:
        return -1
    else:
        return 1
