import unittest
import re

# Standalone pure-function implementations matching system specifications
def validate_gstin_spec(gstin: str) -> bool:
    pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
    return bool(re.match(pattern, gstin))

def calculate_gst_spec(amount: float, tax_tier: str, is_intrastate: bool) -> dict:
    rates = {
        "Essential - 5%": 0.05,
        "Standard - 12%": 0.12,
        "Services - 18%": 0.18,
        "Luxury - 28%": 0.28
    }
    rate = rates.get(tax_tier, 0.18)
    total_tax = round(amount * rate, 2)
    
    if is_intrastate:
        cgst = round(total_tax / 2, 2)
        sgst = round(total_tax / 2, 2)
        igst = 0.0
    else:
        cgst = 0.0
        sgst = 0.0
        igst = total_tax
        
    return {
        "total_tax": total_tax,
        "cgst": cgst,
        "sgst": sgst,
        "igst": igst
    }

class TestGSTAuditEngine(unittest.TestCase):

    def test_valid_gstin(self):
        self.assertTrue(validate_gstin_spec("36AABCB1422R1Z5"))

    def test_invalid_gstin(self):
        self.assertFalse(validate_gstin_spec("INVALID12345"))

    def test_gst_calculation_intrastate(self):
        result = calculate_gst_spec(10000, "Standard - 12%", True)
        self.assertEqual(result['total_tax'], 1200.0)
        self.assertEqual(result['cgst'], 600.0)
        self.assertEqual(result['sgst'], 600.0)
        self.assertEqual(result['igst'], 0.0)

    def test_gst_calculation_interstate(self):
        result = calculate_gst_spec(10000, "Standard - 12%", False)
        self.assertEqual(result['total_tax'], 1200.0)
        self.assertEqual(result['cgst'], 0.0)
        self.assertEqual(result['sgst'], 0.0)
        self.assertEqual(result['igst'], 1200.0)

    def test_16_digit_amount_guardrail(self):
        max_amount = 9999999999999999  # 16 digits
        result = calculate_gst_spec(max_amount, "Standard - 12%", False)
        self.assertEqual(result['total_tax'], 1199999999999999.88)

if __name__ == '__main__':
    unittest.main()
