# 🧾 AI-Driven Financial & GST Audit Engine

An automated, compliance-focused tax evaluation engine powered by the **Strands SDK**, **Ollama**, and **Llama 3.1**. Built for the **AWS First Commit Hackathon**, this application performs deterministic Indian Goods and Services Tax (GST) calculations, statutory tax splitting (CGST, SGST, IGST), and GSTIN format verification while preventing computational hallucinations across multi-billion monetary inputs.

---

## 📌 Core Features

- **Dual Interaction Modes:**
  - **Direct Field Entry Dashboard:** A high-throughput, structured control layout for precise audit evaluation with zero LLM execution overhead.
  - **Single Input Query Mode:** A conversational agent interface that parses raw unstructured financial queries and presents visual metric reports.
- **High-Precision Financial Guardrails:**
  - Supports large-scale corporate invoice amounts up to **16 digits** (₹9,999,999,999,999,999.00 / ₹10 Quadrillion ceiling).
  - Built-in circuit breaker rejecting oversized numerical inputs (17+ digits).
- **Automated Statutory Tax Allocation:**
  - Calculates tax rates based on tier categories (`Essential - 5%`, `Standard - 12%`, `Services - 18%`, `Luxury - 28%`).
  - Computes exact **CGST + SGST** (Intra-State) and **IGST** (Inter-State) allocations.
- **GSTIN Structural Validation:**
  - Standard regex-based pattern matching verifying state code, PAN structure, entity code, and checksum structure.
- **Audit Log Export:**
  - One-click downloadable JSON audit history report containing session logs and calculation breakdowns.

---

## 🏗️ Architecture & Technology Stack

- **Agent Framework:** [Strands SDK](https://github.com/strands-ai/strands)
- **Local LLM Infrastructure:** [Ollama](https://ollama.com/) running `llama3.1`
- **UI Framework:** [Streamlit](https://streamlit.io/)
- **Core Runtime:** Python 3.10+

---

## 🚀 Quickstart Guide

### Prerequisites

1. **Python 3.10+** installed on your system.
2. **Ollama** installed and running locally with `llama3.1`:
   ```bash
   ollama pull llama3.1
1. Installation & Setup
Bash
git clone [https://github.com/barkuntasrinivas2025-stack/gst-audit-engine.git](https://github.com/barkuntasrinivas2025-stack/gst-audit-engine.git)
cd gst-audit-engine
pip install -r requirements.txt
2. Run Application & Unit Tests
Run unit tests:

Bash
python -m unittest test_audit_engine.py
Launch Streamlit GUI:

Bash
streamlit run gui_app.py
📄 License
Distributed under the MIT License. Built for AWS First Commit Hackathon 2026.
