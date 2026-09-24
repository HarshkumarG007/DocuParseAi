import re
from typing import Dict, List

def run_regex_baseline(text_blocks: List[str]) -> Dict[str, str]:
    """
    Baseline 1: Rule-based Regex Extraction.
    Matches dates and total amounts from plain text.
    """
    full_text = " ".join(text_blocks)
    
    results = {
        "vendor": "",
        "date": "",
        "total": ""
    }
    
    # Very naive vendor assumption: first line of text
    if text_blocks:
        results["vendor"] = text_blocks[0]
        
    # Date Regex: DD/MM/YYYY or YYYY-MM-DD
    date_pattern = r'\b(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2})\b'
    date_matches = re.findall(date_pattern, full_text)
    if date_matches:
        results["date"] = date_matches[0]
        
    # Total Regex: find 'total' followed by a currency amount
    total_pattern = r'(?i)total[\s:=]+[\$£€]?\s*(\d+[.,]\d{2})'
    total_matches = re.findall(total_pattern, full_text)
    if total_matches:
        results["total"] = total_matches[-1] # Usually the last total is the grand total
    else:
        # Fallback: largest currency amount
        amount_pattern = r'[\$£€]\s*(\d+[.,]\d{2})|\b(\d+[.,]\d{2})\b'
        amounts = re.findall(amount_pattern, full_text)
        valid_amounts = []
        for amt in amounts:
            val = amt[0] or amt[1]
            try:
                valid_amounts.append(float(val.replace(',', '.')))
            except:
                pass
        if valid_amounts:
            results["total"] = f"{max(valid_amounts):.2f}"
            
    return results
