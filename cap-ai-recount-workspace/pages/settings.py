import streamlit as st

from components.kpi_cards import page_header
from database import crud, init_db
from utils.auth import ROLES, can_access


def render():
    page_header("Settings", "Platform configuration, access control & audit trail")

    tab1, tab2, tab3, tab4 = st.tabs(["👤 User & Role", "📜 Activity Logs", "🔒 Audit Trail", "⚙️ System"])

    with tab1:
        st.markdown("#### Role-Based Access Control")
        roles = list(ROLES.keys())
        selected_role = st.selectbox("Select Role", roles, index=roles.index(st.session_state.get("role", "Auditor")))
        username = st.text_input("Username", value=st.session_state.get("username", "Auditor User"))

        if st.button("Apply Role"):
            st.session_state["role"] = selected_role
            st.session_state["username"] = username
            crud.log_activity(username, selected_role, "Role switched", "Settings")
            st.success(f"Logged in as {username} ({selected_role})")
            st.rerun()

        st.markdown("#### Permission Matrix")
        import pandas as pd
        perm_data = []
        for role, perms in ROLES.items():
            perm_data.append({"Role": role, **{k.replace("_", " ").title(): "✅" if v else "❌" for k, v in perms.items()}})
        st.dataframe(pd.DataFrame(perm_data), use_container_width=True, hide_index=True)

    with tab2:
        logs = crud.get_activity_logs(100)
        if not logs.empty:
            st.dataframe(logs, use_container_width=True, hide_index=True)
        else:
            st.info("No activity logs yet.")

    with tab3:
        audit = crud.get_audit_trail(100)
        if not audit.empty:
            st.dataframe(audit, use_container_width=True, hide_index=True)
        else:
            st.info("No audit trail entries yet.")

    with tab4:
        st.markdown("#### System Configuration")
        st.number_input("Idle Balance Threshold (days)", 30, 365, 60, key="sys_idle_days")
        st.number_input("Balance Threshold (₹)", 10000, 10000000, 100000, key="sys_balance_thresh")
        st.number_input("Round-Trip Return Window (days)", 7, 90, 30, key="sys_rt_window")

        if can_access(st.session_state.get("role", "Auditor"), "settings"):
            if st.button("🔄 Reinitialize Database", type="primary"):
                init_db()
                st.success("Database reinitialized with sample data.")
        else:
            st.caption("Admin access required for system operations.")
