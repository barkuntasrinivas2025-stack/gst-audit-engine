import streamlit as st
import json
import re

st.set_page_config(
    page_title="AI Financial & GST Audit Engine", 
    page_icon="🧾", 
    layout="wide"
)

st.title("🧾 AI-Driven Financial & GST Audit Engine")
st.caption("Strands SDK & Local Llama 3.1 | Automated Compliance & Tax Calculation System")

# Max limit guardrail: 16 digits max (up to 9,999,999,999,999,999.0 INR)
MAX_AUDIT_LIMIT = 9_999_999_999_999_999.0 

# ---------------------------------------------------------
# Core Tools & Functions
# ---------------------------------------------------------
def calculate_gst_core(amount: float, category: str = "services") -> dict:
    """Calculates Indian GST for a given monetary amount up to 16 digits."""
    try:
        num_amount = float(amount)
    except (ValueError, OverflowError):
        return {"error": "Invalid or oversized numerical input provided."}
        
    if num_amount > MAX_AUDIT_LIMIT:
        return {"error": "Amount exceeds maximum allowable single-invoice financial limit (16 digits / ₹10 Quadrillion)."}

    rates = {"essential": 0.05, "standard": 0.12, "services": 0.18, "luxury": 0.28}
    cat = str(category).lower().strip()
    rate = rates.get(cat, 0.18)
    tax_amount = num_amount * rate
    
    return {
        "base_amount": num_amount,
        "category": cat.capitalize(),
        "gst_rate_percent": int(rate * 100),
        "tax_amount": tax_amount,
        "total_amount": num_amount + tax_amount,
        "cgst": tax_amount / 2,
        "sgst": tax_amount / 2,
        "igst": tax_amount
    }

def validate_gstin_core(gstin: str) -> dict:
    """Validates structural format of an Indian GSTIN identification string."""
    clean_gstin = str(gstin).strip().upper()
    gstin_regex = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
    is_valid = bool(re.match(gstin_regex, clean_gstin))
    return {
        "gstin": clean_gstin,
        "is_valid": is_valid,
        "state_code": clean_gstin[:2] if is_valid else "N/A"
    }

# UI Input Sanitizer for Query Mode (Blocks >16 digits, i.e., 17+ digits)
def sanitize_user_input(prompt_text: str):
    huge_numbers = re.findall(r'\b\d{17,}\b', prompt_text)
    if huge_numbers:
        return False, (
            f"⚠️ **Input Error:** The number `{huge_numbers[0][:10]}...` ({len(huge_numbers[0])} digits) "
            f"exceeds the maximum allowable single-invoice financial limit (16 digits). "
            f"Please enter a valid monetary amount."
        )
    return True, prompt_text

def parse_query_text(prompt_text: str):
    """Extracts amount, category, and GSTIN from conversational query string."""
    # Find numbers up to 16 digits
    amounts = re.findall(r'\b\d{1,16}(?:\.\d+)?\b', prompt_text)
    amount = float(amounts[0]) if amounts else 100000.0

    # Categorize based on keywords
    cat = "services"
    lower_p = prompt_text.lower()
    if "essential" in lower_p or "5%" in lower_p:
        cat = "essential"
    elif "standard" in lower_p or "12%" in lower_p:
        cat = "standard"
    elif "luxury" in lower_p or "28%" in lower_p:
        cat = "luxury"
    elif "service" in lower_p or "18%" in lower_p:
        cat = "services"

    # Extract GSTIN if present
    gstin_matches = re.findall(r'[0-9]{2}[A-Za-z]{5}[0-9]{4}[A-Za-z]{1}[1-9A-Za-z]{1}[Zz][0-9A-Za-z]{1}', prompt_text)
    gstin = gstin_matches[0].upper() if gstin_matches else "36AABCU9603R1ZM"

    return amount, cat, gstin

def render_audit_report(gst_res: dict, gstin_res: dict):
    """Renders the standardized visual audit report format."""
    st.markdown("### 📊 Audit & Compliance Evaluation Report")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Base Amount", f"₹{gst_res['base_amount']:,.2f}")
    c2.metric("GST Rate", f"{gst_res['gst_rate_percent']}% ({gst_res['category']})")
    c3.metric("Total Tax Payable", f"₹{gst_res['tax_amount']:,.2f}")
    c4.metric("Final Invoice Total", f"₹{gst_res['total_amount']:,.2f}")

    st.markdown("---")
    st.markdown("### Tax Breakdown & Compliance Status")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("**Statutory Tax Allocation**")
        st.write(f"• **Intra-State (CGST + SGST):** ₹{gst_res['cgst']:,.2f} + ₹{gst_res['sgst']:,.2f}")
        st.write(f"• **Inter-State (IGST):** ₹{gst_res['igst']:,.2f}")
        st.write(f"• **Applied Category Rule:** {gst_res['category']}")

    with col_right:
        st.markdown("**GSTIN Validation Summary**")
        if gstin_res["is_valid"]:
            st.success(f"Valid Format: {gstin_res['gstin']} (State Code: {gstin_res['state_code']})")
        else:
            st.error(f"Invalid GSTIN Format: {gstin_res['gstin']}")

# ---------------------------------------------------------
# Sidebar & Navigation
# ---------------------------------------------------------
st.sidebar.header("Input Controls")
input_mode = st.sidebar.radio("Input Mode", ["Direct Field Entry", "Single Input Query"])

# ---------------------------------------------------------
# Mode 1: Direct Field Entry (Dashboard)
# ---------------------------------------------------------
if input_mode == "Direct Field Entry":
    with st.sidebar:
        amount_input = st.number_input(
            "Invoice Base Amount (₹)", 
            min_value=0.0, 
            max_value=9999999999999999.0, 
            value=100000.0, 
            step=1000.0,
            format="%.2f"
        )
        category_input = st.selectbox(
            "Tax Category", 
            ["services", "essential", "standard", "luxury"]
        )
        gstin_input = st.text_input(
            "GSTIN Identification Number", 
            value="36AABCU9603R1ZM"
        )
        generate_btn = st.button("Generate Audit Report", type="primary")

    if generate_btn or "initial_run" not in st.session_state:
        st.session_state.initial_run = True
        
        gst_res = calculate_gst_core(amount_input, category_input)
        gstin_res = validate_gstin_core(gstin_input)

        if "error" in gst_res:
            st.error(gst_res["error"])
        else:
            render_audit_report(gst_res, gstin_res)

# ---------------------------------------------------------
# Mode 2: Single Input Query (Formatted Dashboard Response)
# ---------------------------------------------------------
else:
    st.info("Single Input Query mode active. Enter invoice details in conversational format below.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous responses
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        elif msg["role"] == "assistant_error":
            with st.chat_message("assistant"):
                st.error(msg["content"])
        elif msg["role"] == "assistant_report":
            with st.chat_message("assistant"):
                render_audit_report(msg["gst_res"], msg["gstin_res"])

    # Chat Input Box
    if prompt := st.chat_input("Enter invoice details (e.g. 'Audit invoice: Amount 1000000000000 INR for services, GSTIN 36AABCU9603R1ZM')"):
        st.session_state.messages.append({"role": "user", "content": str(prompt)})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            is_valid_input, sanitized_msg = sanitize_user_input(str(prompt))
            
            if not is_valid_input:
                st.error(sanitized_msg)
                st.session_state.messages.append({"role": "assistant_error", "content": sanitized_msg})
            else:
                with st.spinner("Processing invoice through audit engine..."):
                    amt, cat, gstin = parse_query_text(sanitized_msg)
                    gst_res = calculate_gst_core(amt, cat)
                    gstin_res = validate_gstin_core(gstin)

                    if "error" in gst_res:
                        st.error(gst_res["error"])
                        st.session_state.messages.append({"role": "assistant_error", "content": gst_res["error"]})
                    else:
                        render_audit_report(gst_res, gstin_res)
                        st.session_state.messages.append({
                            "role": "assistant_report", 
                            "gst_res": gst_res, 
                            "gstin_res": gstin_res
                        })
