import streamlit as st

from components.kpi_cards import page_header
from database import crud
from utils.auth import can_access
from utils.report_generator import generate_pdf_report


def render():
    page_header("Interest & Bank Charge Validation", "Recompute bank charges and interest against sanctioned terms")

    if not can_access(st.session_state.get("role", "Auditor"), "interest"):
        st.warning("Your role does not have access to this module.")
        return

    df = crud.get_interest_validations()

    if not df.empty:
        display = df[["account", "principal", "rate", "time_days", "expected_interest", "actual_interest", "variance_pct", "status"]].copy()
        display.columns = ["Account", "Principal", "Rate", "Time (Days)", "Expected Interest", "Actual Interest", "Variance %", "Status"]

        def highlight_variance(row):
            styles = [""] * len(row)
            if row["Status"] == "Overcharge":
                styles = ["background-color: rgba(255,107,107,0.15)"] * len(row)
            elif row["Status"] == "Undercharge":
                styles = ["background-color: rgba(255,179,71,0.15)"] * len(row)
            return styles

        st.dataframe(display.style.apply(highlight_variance, axis=1), use_container_width=True, hide_index=True)

        over = len(display[display["Status"] == "Overcharge"])
        under = len(display[display["Status"] == "Undercharge"])
        ok = len(display[display["Status"] == "OK"])

        c1, c2, c3 = st.columns(3)
        c1.metric("Overcharges", over)
        c2.metric("Undercharges", under)
        c3.metric("Within Tolerance", ok)

        st.markdown("---")
        st.markdown("#### Download Audit Report")
        pdf_bytes = generate_pdf_report("Interest Validation Audit Report")
        st.download_button("📥 Download PDF Audit Report", pdf_bytes, "interest_audit_report.pdf", "application/pdf")
    else:
        st.info("Upload interest validation data via Excel Import Center.")

    with st.expander("ℹ️ Calculation Formula"):
        st.latex(r"\text{Expected Interest} = \text{Principal} \times \text{Rate} \times \frac{\text{Time (Days)}}{365}")
