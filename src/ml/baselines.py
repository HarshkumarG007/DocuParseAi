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
        "subtotal": "",
        "tax": "",
        "total": ""
    }
    
    # Vendor extraction: First 2-3 tokens if they appear to be text
    if text_blocks:
        candidate_words = []
        for word in text_blocks[:6]:
            if word.lower() in {"date:", "date", "receipt", "invoice", "order", "tax", "total", "subtotal"}:
                break
            if not re.search(r'\d', word):
                candidate_words.append(word)
            if len(candidate_words) >= 3:
                break
        results["vendor"] = " ".join(candidate_words) if candidate_words else text_blocks[0]
        
    # Date Regex: DD/MM/YYYY, YYYY-MM-DD, or DD-MM-YYYY
    date_pattern = r'\b(\d{4}[/-]\d{2}[/-]\d{2}|\d{2}[/-]\d{2}[/-]\d{4})\b'
    date_matches = re.findall(date_pattern, full_text)
    if date_matches:
        results["date"] = date_matches[0]

    # Subtotal Regex
    subtotal_pattern = r'(?i)sub[\s-]?total[\s:=]+[\$£€]?\s*(\d+[.,]\d{2})'
    subtotal_matches = re.findall(subtotal_pattern, full_text)
    if subtotal_matches:
        results["subtotal"] = subtotal_matches[0]

    # Tax Regex
    tax_pattern = r'(?i)\b(?:tax|vat|gst)\b[\s:=]+[\$£€]?\s*(\d+[.,]\d{2})'
    tax_matches = re.findall(tax_pattern, full_text)
    if tax_matches:
        results["tax"] = tax_matches[0]
        
    # Total Regex: find 'total' followed by a currency amount
    total_pattern = r'(?i)\b(?:grand\s+)?total\b[\s:=]+[\$£€]?\s*(\d+[.,]\d{2})'
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
