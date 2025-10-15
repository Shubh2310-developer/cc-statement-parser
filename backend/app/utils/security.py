"""Security utilities for PII redaction and data masking.

This module provides functions to mask sensitive information like
card numbers, account numbers, and other personally identifiable information.
"""

import re
from typing import Optional


def mask_card_number(
    card_number: str,
    show_last: int = 4,
    mask_char: str = "X",
) -> str:
    """Mask a credit card number, showing only the last N digits.

    Args:
        card_number: Credit card number to mask
        show_last: Number of digits to show at the end
        mask_char: Character to use for masking

    Returns:
        Masked card number (e.g., "XXXX XXXX XXXX 1234")
    """
    # Remove any non-digit characters
    digits = re.sub(r"\D", "", card_number)

    if len(digits) < show_last:
        # If card number is too short, mask everything
        return mask_char * len(digits)

    # Calculate how many digits to mask
    mask_count = len(digits) - show_last

    # Create masked version
    masked = mask_char * mask_count + digits[-show_last:]

    # Format with spaces (groups of 4)
    formatted = " ".join([masked[i : i + 4] for i in range(0, len(masked), 4)])

    return formatted


def mask_account_number(
    account_number: str,
    show_last: int = 4,
    mask_char: str = "X",
) -> str:
    """Mask an account number, showing only the last N digits.

    Args:
        account_number: Account number to mask
        show_last: Number of digits to show at the end
        mask_char: Character to use for masking

    Returns:
        Masked account number
    """
    # Remove any non-digit characters
    digits = re.sub(r"\D", "", account_number)

    if len(digits) < show_last:
        return mask_char * len(digits)

    mask_count = len(digits) - show_last
    return mask_char * mask_count + digits[-show_last:]


def mask_email(email: str, mask_char: str = "*") -> str:
    """Mask an email address, showing only first character and domain.

    Args:
        email: Email address to mask
        mask_char: Character to use for masking

    Returns:
        Masked email (e.g., "j***@example.com")
    """
    if "@" not in email:
        # Invalid email, mask everything
        return mask_char * len(email)

    local, domain = email.rsplit("@", 1)

    if len(local) <= 1:
        masked_local = mask_char
    else:
        # Show first character, mask the rest
        masked_local = local[0] + mask_char * (len(local) - 1)

    return f"{masked_local}@{domain}"


def mask_phone_number(
    phone: str,
    show_last: int = 4,
    mask_char: str = "X",
) -> str:
    """Mask a phone number, showing only the last N digits.

    Args:
        phone: Phone number to mask
        show_last: Number of digits to show at the end
        mask_char: Character to use for masking

    Returns:
        Masked phone number
    """
    # Remove any non-digit characters
    digits = re.sub(r"\D", "", phone)

    if len(digits) < show_last:
        return mask_char * len(digits)

    mask_count = len(digits) - show_last
    masked = mask_char * mask_count + digits[-show_last:]

    # Format with common phone pattern
    if len(masked) == 10:
        return f"{masked[:3]}-{masked[3:6]}-{masked[6:]}"
    else:
        return masked


def mask_name(name: str, mask_char: str = "*") -> str:
    """Mask a name, showing only first letters.

    Args:
        name: Name to mask
        mask_char: Character to use for masking

    Returns:
        Masked name (e.g., "J*** D**")
    """
    words = name.split()
    masked_words = []

    for word in words:
        if len(word) == 0:
            continue
        elif len(word) == 1:
            masked_words.append(word)
        else:
            masked_words.append(word[0] + mask_char * (len(word) - 1))

    return " ".join(masked_words)


def redact_pii(text: str, mask_char: str = "X") -> str:
    """Redact personally identifiable information from text.

    This function attempts to find and mask:
    - Credit card numbers
    - Email addresses
    - Phone numbers
    - Potential account numbers

    Args:
        text: Text containing potential PII
        mask_char: Character to use for masking

    Returns:
        Text with PII redacted
    """
    # Mask credit card numbers (13-19 digits with optional spaces/dashes)
    text = re.sub(
        r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{3,4}\b",
        lambda m: mask_card_number(m.group(0), mask_char=mask_char),
        text,
    )

    # Mask email addresses
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        lambda m: mask_email(m.group(0), mask_char=mask_char),
        text,
    )

    # Mask phone numbers (various formats)
    phone_patterns = [
        r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # 123-456-7890
        r"\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b",  # (123) 456-7890
        r"\b\+\d{1,3}[\s.-]?\d{10}\b",  # +91 1234567890
    ]

    for pattern in phone_patterns:
        text = re.sub(
            pattern,
            lambda m: mask_phone_number(m.group(0), mask_char=mask_char),
            text,
        )

    return text


def extract_card_number(text: str) -> Optional[str]:
    """Extract credit card number from text.

    Args:
        text: Text potentially containing a card number

    Returns:
        Card number if found, None otherwise
    """
    # Pattern for card numbers (13-19 digits with optional spaces/dashes)
    pattern = r"\b(\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{3,4})\b"
    match = re.search(pattern, text)

    if match:
        # Return digits only
        return re.sub(r"\D", "", match.group(1))

    return None


def validate_card_number_luhn(card_number: str) -> bool:
    """Validate a credit card number using the Luhn algorithm.

    Args:
        card_number: Card number to validate (digits only)

    Returns:
        True if valid according to Luhn algorithm, False otherwise
    """
    # Remove non-digits
    digits = re.sub(r"\D", "", card_number)

    if not digits or not digits.isdigit():
        return False

    # Luhn algorithm
    total = 0
    reverse_digits = digits[::-1]

    for i, digit in enumerate(reverse_digits):
        n = int(digit)

        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9

        total += n

    return total % 10 == 0


def get_card_type(card_number: str) -> Optional[str]:
    """Identify credit card type from the card number.

    Args:
        card_number: Card number (digits only)

    Returns:
        Card type (VISA, MASTERCARD, AMEX, etc.) or None if unknown
    """
    # Remove non-digits
    digits = re.sub(r"\D", "", card_number)

    if not digits:
        return None

    # Card type patterns (BIN ranges)
    if digits.startswith("4"):
        return "VISA"
    elif digits.startswith(("51", "52", "53", "54", "55")):
        return "MASTERCARD"
    elif digits.startswith(("34", "37")):
        return "AMEX"
    elif digits.startswith(("6011", "65")):
        return "DISCOVER"
    elif digits.startswith(("35", "36", "37", "38", "39")):
        return "DINERS"
    elif digits.startswith("62"):
        return "UNIONPAY"
    elif digits.startswith(("60", "65")):
        return "RUPAY"
    else:
        return "UNKNOWN"


def sanitize_for_logging(data: dict, sensitive_keys: list[str] = None) -> dict:
    """Sanitize a dictionary for logging by masking sensitive values.

    Args:
        data: Dictionary to sanitize
        sensitive_keys: List of keys to mask (case-insensitive)

    Returns:
        Sanitized copy of the dictionary
    """
    if sensitive_keys is None:
        sensitive_keys = [
            "password",
            "secret",
            "token",
            "api_key",
            "card_number",
            "cvv",
            "pin",
            "account_number",
        ]

    # Convert to lowercase for comparison
    sensitive_keys_lower = [k.lower() for k in sensitive_keys]

    def sanitize_value(key: str, value):
        """Recursively sanitize values."""
        if isinstance(value, dict):
            return sanitize_for_logging(value, sensitive_keys)
        elif isinstance(value, list):
            return [sanitize_value(key, item) for item in value]
        elif any(sensitive in key.lower() for sensitive in sensitive_keys_lower):
            # Mask sensitive value
            if isinstance(value, str):
                if len(value) <= 4:
                    return "***"
                return value[:2] + "***" + value[-2:]
            else:
                return "***"
        else:
            return value

    return {key: sanitize_value(key, value) for key, value in data.items()}


def mask_text_pattern(
    text: str,
    pattern: str,
    show_chars: int = 4,
    mask_char: str = "X",
) -> str:
    """Mask text matching a specific regex pattern.

    Args:
        text: Text to search and mask
        pattern: Regex pattern to match
        show_chars: Number of characters to show at the end
        mask_char: Character to use for masking

    Returns:
        Text with matched patterns masked
    """

    def mask_match(match):
        matched_text = match.group(0)
        if len(matched_text) <= show_chars:
            return mask_char * len(matched_text)
        mask_count = len(matched_text) - show_chars
        return mask_char * mask_count + matched_text[-show_chars:]

    return re.sub(pattern, mask_match, text)
