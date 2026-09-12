import streamlit as st
import json
from app_agent import parse_financial_query, validate_gstin, calculate_gst

# Page Configuration
st.set_page_config(
    page_title="AI Financial & GST Audit Engine",
    page_icon="🧾",
    layout="wide"
)

# Custom CSS to prevent text truncation on large numbers in st.metric
st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        white-space: normal !important;
        word-break: break-word !important;
        overflow-wrap: anywhere !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧾 AI-Driven Financial & GST Audit Engine")
st.caption("Strands SDK & Local Llama 3.1 | Automated Compliance & Tax Calculation System")

# Sidebar Controls
st.sidebar.header("Input Controls")
input_mode = st.sidebar.radio("Input Mode", ["Direct Field Entry", "Single Input Query"])

if input_mode == "Direct Field Entry":
    amount = st.sidebar.number_input("Invoice Base Amount (₹)", min_value=0.0, max_value=9999999999999999.0, value=10000000000000000.0, step=1000.0)
    category = st.sidebar.selectbox("Tax Category", ["essential", "standard", "services", "luxury"])
    gstin = st.sidebar.text_input("GSTIN Identification Number", value="36AABCU9603R1ZM")
    generate_btn = st.sidebar.button("Generate Audit Report")
    
    tier_map = {
        "essential": "Essential - 5%",
        "standard": "Standard - 12%",
        "services": "Services - 18%",
        "luxury": "Luxury - 28%"
    }
    
    tier = tier_map[category]
    is_valid_gstin = validate_gstin(gstin)
    tax_data = calculate_gst(amount, tier, is_intrastate=True)
    
    # Audit Report Presentation
    st.subheader("📊 Audit & Compliance Evaluation Report")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Base Amount", f"₹{amount:,.2f}")
    c2.metric("GST Rate", f"18% (Services)")
    c3.metric("Total Tax Payable", f"₹{tax_data['total_tax']:,.2f}")
    c4.metric("Final Invoice Total", f"₹{(amount + tax_data['total_tax']):,.2f}")
    
    st.divider()
    st.subheader("Tax Breakdown & Compliance Status")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Statutory Tax Allocation**")
        st.write(f"• **Intra-State (CGST + SGST):** ₹{tax_data['cgst']:,.2f} + ₹{tax_data['sgst']:,.2f}")
        st.write(f"• **Inter-State (IGST):** ₹{tax_data['igst']:,.2f}")
        st.write(f"• **Applied Category Rule:** Services")
        
    with col2:
        st.markdown("**GSTIN Validation Summary**")
        if is_valid_gstin:
            st.success(f"Valid Format: {gstin} (State Code: {gstin[:2]})")
        else:
            st.error(f"Invalid GSTIN Format: {gstin}")

else:
    st.info("Single Input Query mode active. Enter invoice details in conversational format below.")
    query = st.text_input("Enter invoice details (e.g. 'Audit invoice: Amount 9,999,999,999,999,999 INR for services, GSTIN 36AABCU9603R1ZM')", key="query_input")
    
    if query:
        parsed = parse_financial_query(query)
        if "error" in parsed:
            st.error(parsed["error"])
        else:
            amount = parsed["amount"]
            gstin = parsed["gstin"]
            tier = parsed["tier"]
            is_valid_gstin = validate_gstin(gstin)
            tax_data = calculate_gst(amount, tier, parsed["is_intrastate"])
            
            st.subheader("📊 Audit & Compliance Evaluation Report")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Base Amount", f"₹{amount:,.2f}")
            c2.metric("GST Rate", tier)
            c3.metric("Total Tax Payable", f"₹{tax_data['total_tax']:,.2f}")
            c4.metric("Final Invoice Total", f"₹{(amount + tax_data['total_tax']):,.2f}")
            
            st.divider()
            st.subheader("Tax Breakdown & Compliance Status")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Statutory Tax Allocation**")
                st.write(f"• **Intra-State (CGST + SGST):** ₹{tax_data['cgst']:,.2f} + ₹{tax_data['sgst']:,.2f}")
                st.write(f"• **Inter-State (IGST):** ₹{tax_data['igst']:,.2f}")
                st.write(f"• **Applied Category Rule:** {tier.split('-')[0].strip()}")
            with col2:
                st.markdown("**GSTIN Validation Summary**")
                if is_valid_gstin:
                    st.success(f"Valid Format: {gstin} (State Code: {gstin[:2]})")
                else:
                    st.error(f"Invalid GSTIN Format: {gstin}")
