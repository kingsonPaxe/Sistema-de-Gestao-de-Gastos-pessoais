"""
Currency utilities for formatting Angolan Kwanza (Kz).
Provides functions to format, parse and display currency values consistently.
"""

from decimal import Decimal, InvalidOperation
from typing import Union


def format_kwanza(value: Union[int, float, str, Decimal], include_symbol: bool = True) -> str:
    """
    Format a numerical value as Angolan Kwanza currency.
    
    Examples:
        >>> format_kwanza(1500)
        'Kz 1.500,00'
        >>> format_kwanza(25000)
        'Kz 25.000,00'
        >>> format_kwanza(1250000.75)
        'Kz 1.250.000,75'
        >>> format_kwanza(150.5, include_symbol=False)
        '150,50'
    
    Args:
        value: The amount to format (int, float, string, or Decimal)
        include_symbol: Whether to include 'Kz ' prefix (default: True)
    
    Returns:
        Formatted string in Angolan currency format
    """
    try:
        # Convert to Decimal for precision
        if isinstance(value, str):
            # Handle both '1500.00' and '1500,00' formats
            clean_value = value.replace(',', '.')
            decimal_value = Decimal(clean_value)
        else:
            decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return 'Kz 0,00' if include_symbol else '0,00'
    
    # Format with 2 decimal places: European style (. for thousands, , for decimals)
    formatted = _format_number_european(decimal_value)
    
    return f'Kz {formatted}' if include_symbol else formatted


def parse_kwanza(value: str) -> Decimal:
    """
    Parse a Kwanza-formatted string back to Decimal.
    
    Examples:
        >>> parse_kwanza('Kz 1.500,00')
        Decimal('1500.00')
        >>> parse_kwanza('25.000,75')
        Decimal('25000.75')
        >>> parse_kwanza('150,50')
        Decimal('150.50')
    
    Args:
        value: String formatted as Kwanza currency
    
    Returns:
        Decimal value
    """
    try:
        # Remove 'Kz' symbol and whitespace
        clean = value.replace('Kz', '').strip()
        
        # Convert European format (. for thousands, , for decimals) to standard
        # Remove thousands separators (.) and replace decimal separator (,) with (.)
        clean = clean.replace('.', '')  # Remove thousands separator
        clean = clean.replace(',', '.')  # Convert decimal separator
        
        return Decimal(clean)
    except (InvalidOperation, ValueError, AttributeError):
        return Decimal('0')


def format_currency_minimal(value: Union[int, float, str, Decimal]) -> str:
    """
    Format currency without symbol - returns just the number.
    
    Args:
        value: The amount to format
    
    Returns:
        Formatted number string in European style
    """
    return format_kwanza(value, include_symbol=False)


def _format_number_european(decimal_value: Decimal) -> str:
    """
    Format a Decimal number using European style:
    - Dot (.) for thousands separator
    - Comma (,) for decimal separator
    - 2 decimal places
    
    Args:
        decimal_value: Decimal value to format
    
    Returns:
        Formatted string
    """
    # Quantize to 2 decimal places
    quantized = decimal_value.quantize(Decimal('0.01'))
    
    # Split into integer and decimal parts
    int_part, dec_part = str(quantized).split('.')
    
    # Format integer part with thousands separator (.)
    int_formatted = _add_thousands_separator(int_part)
    
    # Combine with comma as decimal separator
    return f'{int_formatted},{dec_part}'


def _add_thousands_separator(number_str: str) -> str:
    """
    Add thousands separator (.) to a number string.
    
    Examples:
        >>> _add_thousands_separator('1500')
        '1.500'
        >>> _add_thousands_separator('25000')
        '25.000'
        >>> _add_thousands_separator('1250000')
        '1.250.000'
    
    Args:
        number_str: String of digits, potentially with leading minus
    
    Returns:
        String with thousands separators
    """
    # Handle negative numbers
    is_negative = number_str.startswith('-')
    if is_negative:
        number_str = number_str[1:]
    
    # Add separators from right to left
    result = ''
    for i, digit in enumerate(reversed(number_str)):
        if i > 0 and i % 3 == 0:
            result = '.' + result
        result = digit + result
    
    return ('-' + result) if is_negative else result


# Jinja filter compatibility
def kwanza_filter(value: Union[int, float, str, Decimal]) -> str:
    """
    Jinja filter for formatting Kwanza currency.
    Register with: app.jinja_env.filters['kwanza'] = kwanza_filter
    
    Usage in templates:
        {{ balance|kwanza }}
        {{ 1500|kwanza }}
    
    Args:
        value: The amount to format
    
    Returns:
        Formatted Kwanza string
    """
    return format_kwanza(value)


def date_filter(date_obj, format_str: str = '%d/%m/%Y') -> str:
    """
    Jinja filter for formatting dates in Angolan style.
    Register with: app.jinja_env.filters['format_date'] = date_filter
    
    Usage in templates:
        {{ transaction.date|format_date }}
        {{ now|format_date('%d/%m/%Y') }}
    
    Args:
        date_obj: Date object to format
        format_str: Format string (default: dd/mm/yyyy)
    
    Returns:
        Formatted date string
    """
    if not date_obj:
        return ''
    try:
        return date_obj.strftime(format_str)
    except (AttributeError, ValueError):
        return str(date_obj)
