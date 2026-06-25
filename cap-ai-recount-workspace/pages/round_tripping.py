import streamlit as st

from components.kpi_cards import page_header
from database import crud
from utils.auth import can_access
from utils.round_trip_detection import build_network_graph, detect_round_tripping, risk_color


def render():
    page_header("Fund Round-Tripping Detection", "Identify circular transfers and related account activity")

    if not can_access(st.session_state.get("role", "Auditor"), "round_trip"):
        st.warning("Your role does not have access to this module.")
        return

    col1, col2 = st.columns([2, 1])
    with col2:
        return_window = st.slider("Return Window (days)", 7, 90, 30)
        if st.button("🔍 Run Detection", type="primary", use_container_width=True):
            st.session_state["rt_run"] = True

    txn_df = crud.get_transactions()
    if txn_df.empty:
        st.info("Import transaction data via Excel Import Center.")
        return

    display_txn = txn_df[["transaction_id", "txn_date", "from_account", "to_account", "amount"]].copy()
    display_txn.columns = ["Transaction ID", "Date", "From Account", "To Account", "Amount"]
    st.markdown("#### Transaction Data")
    st.dataframe(display_txn, use_container_width=True, hide_index=True)

    if st.session_state.get("rt_run", True):
        with st.spinner("Analyzing round-tripping patterns..."):
            risk_df = detect_round_tripping(display_txn, return_window)

        if not risk_df.empty:
            st.markdown("#### Risk Score Table")

            def style_risk(val):
                color = risk_color(val)
                return f"color: {color}; font-weight: bold"

            styled = risk_df.style.map(style_risk, subset=["Risk Score"])
            st.dataframe(styled, use_container_width=True, hide_index=True)

            st.markdown(
                f'<span class="risk-low">● Low (&lt;40)</span> &nbsp; '
                f'<span class="risk-medium">● Medium (40-69)</span> &nbsp; '
                f'<span class="risk-high">● High (≥70)</span>',
                unsafe_allow_html=True,
            )
        else:
            st.success("No round-tripping patterns detected.")

        st.markdown("#### Network Graph — Money Flow")
        st.plotly_chart(build_network_graph(display_txn), use_container_width=True)
