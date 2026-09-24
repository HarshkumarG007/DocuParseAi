import dateparser
import re
from typing import Optional

def normalize_date(date_str: str) -> Optional[str]:
    """
    Parse a variety of date formats and return YYYY-MM-DD.
    Returns None if parsing fails.
    """
    if not date_str:
        return None
        
    # Clean up common OCR noise before parsing
    cleaned = re.sub(r'[^\w\s/:.,-]', '', date_str).strip()
    
    # dateparser handles a massive variety of formats automatically
    parsed_date = dateparser.parse(cleaned, settings={'STRICT_PARSING': False})
    
    if parsed_date:
        return parsed_date.strftime("%Y-%m-%d")
    return None

def normalize_currency(currency_str: str) -> Optional[float]:
    """
    Strip currency symbols, handle OCR typos (O -> 0, l -> 1),
    and convert to float.
    """
    if not currency_str:
        return None
        
    # Replace common OCR typos
    cleaned = currency_str.replace('O', '0').replace('o', '0').replace('l', '1').replace('I', '1')
    
    # Remove currency symbols and spaces
    cleaned = re.sub(r'[\$£€\s]', '', cleaned)
    
    # Handle European comma decimals vs US dot decimals
    # E.g. "1.234,56" -> "1234.56"
    # Or "1,234.56" -> "1234.56"
    
    # Extract only numbers, commas, and dots
    cleaned = re.sub(r'[^\d.,]', '', cleaned)
    
    if not cleaned:
        return None
        
    # If both comma and dot exist, the last one is likely the decimal separator
    if ',' in cleaned and '.' in cleaned:
        last_comma = cleaned.rfind(',')
        last_dot = cleaned.rfind('.')
        if last_comma > last_dot:
            # Comma is decimal
            cleaned = cleaned.replace('.', '')
            cleaned = cleaned.replace(',', '.')
        else:
            # Dot is decimal
            cleaned = cleaned.replace(',', '')
    elif ',' in cleaned:
        # Only comma exists, check if it's a decimal (e.g. 12,50)
        parts = cleaned.split(',')
        if len(parts) == 2 and len(parts[1]) in (1, 2):
            cleaned = cleaned.replace(',', '.')
        else:
            cleaned = cleaned.replace(',', '')
            
    try:
        return float(cleaned)
    except ValueError:
        return None
