import streamlit as st

from components.kpi_cards import page_header
from utils.auth import can_access
from utils.report_generator import generate_excel_report, generate_pdf_report, generate_risk_summary


def render():
    page_header("Reporting Center", "Generate executive audit reports with findings and recommendations")

    if not can_access(st.session_state.get("role", "Auditor"), "reports"):
        st.warning("Your role does not have access to this module.")
        return

    st.markdown(
        """
        <div class="glass-card">
            Generate comprehensive audit reports including executive summary,
            charts, findings, and recommendations — branded with CAP AI.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 📄 PDF Report")
        st.caption("Executive summary with KPIs and recommendations")
        pdf = generate_pdf_report()
        st.download_button("Download PDF", pdf, "cap_ai_audit_report.pdf", "application/pdf", use_container_width=True)

    with col2:
        st.markdown("#### 📊 Excel Report")
        st.caption("Full data export across all modules")
        excel = generate_excel_report()
        st.download_button("Download Excel", excel, "cap_ai_full_report.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

    with col3:
        st.markdown("#### ⚠️ Risk Summary")
        st.caption("Consolidated risk findings report")
        risk = generate_risk_summary()
        st.download_button("Download Risk Summary", risk, "cap_ai_risk_summary.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

    st.markdown("---")
    st.markdown("#### Report Contents")
    st.markdown("""
    - **Executive Summary** — Platform-wide audit overview
    - **KPI Dashboard** — Key metrics and trends
    - **Findings** — Suspicious transactions, idle balances, interest deviations
    - **Recommendations** — Prioritized action items for compliance
    """)
