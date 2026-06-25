import streamlit as st

from components.kpi_cards import page_header
from database import crud
from utils.auth import can_access
from utils.signatory_check import verify_signatories


def render():
    page_header("Signatory Verification", "Verify authorized signatories versus actual transaction approvers")

    if not can_access(st.session_state.get("role", "Auditor"), "signatory"):
        st.warning("Your role does not have access to this module.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Authorized Signatories")
        sig_df = crud.get_signatories()
        if not sig_df.empty:
            display = sig_df[["account", "authorized_signatory"]].copy()
            display.columns = ["Account", "Authorized Signatory"]
            st.dataframe(display, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("#### Transaction Approvers")
        txn_df = crud.get_transactions()
        if not txn_df.empty:
            display = txn_df[["transaction_id", "approved_by"]].dropna().copy()
            display.columns = ["Transaction ID", "Approved By"]
            st.dataframe(display, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### Risk Matrix")

    issues = verify_signatories()
    if not issues.empty:
        st.dataframe(issues, use_container_width=True, hide_index=True)

        unauthorized = len(issues[issues["Issue"].str.contains("Unauthorized", na=False)])
        missing = len(issues[issues["Issue"].str.contains("Missing", na=False)])
        c1, c2 = st.columns(2)
        c1.metric("Unauthorized Approvals", unauthorized)
        c2.metric("Missing Approvals", missing)
    else:
        st.success("All signatory verifications passed.")
