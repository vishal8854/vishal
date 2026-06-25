import streamlit as st

from components.kpi_cards import page_header
from database import crud
from utils.auth import can_access


def render():
    page_header("Idle Balance Monitoring", "Flag idle balances that should have been swept or invested")

    if not can_access(st.session_state.get("role", "Auditor"), "idle"):
        st.warning("Your role does not have access to this module.")
        return

    df = crud.get_idle_accounts()

    if not df.empty:
        total_idle = df["balance"].sum()
        at_risk = len(df[df["idle_days"] > 90])

        c1, c2 = st.columns(2)
        c1.metric("Total Idle Funds", f"₹{total_idle:,.0f}")
        c2.metric("Accounts at Risk (>90 days)", at_risk)

        display = df[["account", "balance", "last_transaction_date", "idle_days", "recommendation"]].copy()
        display.columns = ["Account", "Balance", "Last Transaction Date", "Idle Days", "Recommendation"]

        def rec_color(row):
            rec = row["Recommendation"]
            if rec == "Invest in FD":
                return ["background-color: rgba(255,107,107,0.12)"] * len(row)
            if rec == "Sweep Account":
                return ["background-color: rgba(255,179,71,0.12)"] * len(row)
            return ["background-color: rgba(100,255,218,0.08)"] * len(row)

        st.dataframe(display.style.apply(rec_color, axis=1), use_container_width=True, hide_index=True)
    else:
        st.info("No idle accounts flagged. Upload data via Excel Import Center.")

    with st.expander("⚙️ Monitoring Rules"):
        st.markdown("- **No activity** for configurable X days (default: 60)")
        st.markdown("- **Balance exceeds** threshold (default: ₹100,000)")
        st.markdown("- Recommendations: Sweep Account | Invest in FD | Review Account")
