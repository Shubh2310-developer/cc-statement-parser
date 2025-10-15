"""
Formatting utilities for currency, dates, and numbers
"""
from config import CURRENCY_SYMBOL, CURRENCY_SYMBOL_ALT

def format_currency(amount, symbol=CURRENCY_SYMBOL, use_alt=False):
    """Format amount as currency with proper symbol and separators"""
    if use_alt:
        symbol = CURRENCY_SYMBOL_ALT
    
    # Handle negative amounts
    if amount < 0:
        return f"-{symbol}{abs(amount):,.2f}"
    return f"{symbol}{amount:,.2f}"

def format_indian_currency(amount):
    """Format currency in Indian numbering system (lakhs/crores)"""
    s = f"{abs(amount):.2f}"
    parts = s.split('.')
    integer_part = parts[0]
    decimal_part = parts[1]
    
    # Indian numbering: Last 3 digits, then groups of 2
    if len(integer_part) <= 3:
        formatted = integer_part
    else:
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        
        # Group remaining digits in pairs from right to left
        groups = []
        while remaining:
            groups.append(remaining[-2:])
            remaining = remaining[:-2]
        
        formatted = ','.join(reversed(groups)) + ',' + last_three
    
    result = f"{CURRENCY_SYMBOL}{formatted}.{decimal_part}"
    
    if amount < 0:
        return f"-{result}"
    return result

def format_percentage(value, decimals=2):
    """Format value as percentage"""
    return f"{value:.{decimals}f} %"

def format_account_number(number, mask=True):
    """Format account/card number with masking"""
    number_str = str(number)
    if mask and len(number_str) > 4:
        masked = 'X' * (len(number_str) - 4) + number_str[-4:]
        # Add spaces every 4 digits
        return ' '.join([masked[i:i+4] for i in range(0, len(masked), 4)])
    return ' '.join([number_str[i:i+4] for i in range(0, len(number_str), 4)])

def format_date(date_str):
    """Format date string consistently"""
    return date_str

def format_amount_with_sign(amount):
    """Format amount with explicit + or - sign"""
    if amount >= 0:
        return f"+{format_currency(amount)}"
    return format_currency(amount)
