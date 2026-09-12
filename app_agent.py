import json
import re
from strands import Agent, tool
from strands.models.ollama import OllamaModel

@tool
def calculate_gst(amount: float, category: str = "services") -> dict:
    """Calculates Indian GST for a given monetary amount.
    
    Args:
        amount: The base numerical invoice amount (e.g. 12500.0).
        category: Must be one of 'essential', 'standard', 'services', or 'luxury'. Defaults to 'services'.
    """
    rates = {
        "essential": 0.05,
        "standard": 0.12,
        "services": 0.18,
        "luxury": 0.28
    }
    cat = str(category).lower().strip()
    rate = rates.get(cat, 0.18)
    tax_amount = float(amount) * rate
    
    return {
        "base_amount": float(amount),
        "category": cat,
        "gst_rate_percent": int(rate * 100),
        "tax_amount": tax_amount,
        "total_amount": float(amount) + tax_amount
    }

@tool
def validate_gstin_format(gstin: str) -> dict:
    """Validates the structural format of an Indian GSTIN identification string.
    
    Args:
        gstin: A 15-character Indian GSTIN string (e.g. '36AABCU9603R1ZM').
    """
    clean_gstin = str(gstin).strip().upper()
    gstin_regex = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
    is_valid = bool(re.match(gstin_regex, clean_gstin))
    
    return {
        "gstin": clean_gstin,
        "is_structurally_valid": is_valid,
        "state_code": clean_gstin[:2] if is_valid else "INVALID"
    }

# Local Ollama configuration
ollama_model = OllamaModel(
    host="http://localhost:11434",
    model_id="llama3.1"
)

# Explicit system prompt constraining argument choices
system_instruction = (
    "You are a precise Indian GST tax auditor. "
    "To audit an invoice: "
    "1. Validate the GSTIN using validate_gstin_format. "
    "2. Calculate tax using calculate_gst with amount and category ('services', 'essential', 'standard', or 'luxury'). "
    "Do NOT invent extra parameters like state_code or gst_rate when calling calculate_gst."
)

agent = Agent(
    model=ollama_model,
    tools=[calculate_gst, validate_gstin_format],
    system_prompt=system_instruction
)

if __name__ == "__main__":
    query = "Audit this invoice: Amount is 12500 INR for services. Vendor GSTIN is 36AABCU9603R1ZM."
    print("--- Running Audit Agent ---")
    response = agent(query)
    print("\n--- Final Agent Response ---")
    print(response)
