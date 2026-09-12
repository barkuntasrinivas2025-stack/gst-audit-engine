import re

def validate_gstin(gstin: str) -> bool:
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    return bool(re.match(pattern, gstin))

def calculate_gst(amount: float, tier: str, is_intrastate: bool = True) -> dict:
    rates = {
        "Essential - 5%": 0.05,
        "Standard - 12%": 0.12,
        "Services - 18%": 0.18,
        "Luxury - 28%": 0.28
    }
    rate = rates.get(tier, 0.18)
    total_tax = amount * rate
    if is_intrastate:
        cgst = total_tax / 2
        sgst = total_tax / 2
        igst = 0.0
    else:
        cgst = 0.0
        sgst = 0.0
        igst = total_tax
    return {
        "base_amount": amount,
        "rate": rate,
        "total_tax": total_tax,
        "cgst": cgst,
        "sgst": sgst,
        "igst": igst
    }

def parse_financial_query(query_str: str) -> dict:
    gstin_match = re.search(r'\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b', query_str)
    gstin = gstin_match.group(0) if gstin_match else "36AABCU9603R1ZM"

    clean_query = re.sub(r'(?<=\d),(?=\d)', '', query_str)
    amount_matches = re.findall(r'\b\d{1,16}(?:\.\d{1,2})?\b', clean_query)

    amount = 0.0
    if amount_matches:
        amount = max([float(m) for m in amount_matches])

    raw_digits = re.findall(r'\b\d{17,}\b', clean_query)
    if raw_digits:
        return {"error": "Input amount exceeds safety threshold (16-digit max limit / INR 10 Quadrillion)."}

    tier = "Services - 18%"
    if "essential" in query_str.lower() or "5%" in query_str:
        tier = "Essential - 5%"
    elif "standard" in query_str.lower() or "12%" in query_str:
        tier = "Standard - 12%"
    elif "luxury" in query_str.lower() or "28%" in query_str:
        tier = "Luxury - 28%"

    is_intrastate = "inter" not in query_str.lower()

    return {
        "amount": amount,
        "gstin": gstin,
        "tier": tier,
        "is_intrastate": is_intrastate
    }
