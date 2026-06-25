import streamlit as st

from components.sidebar import render_sidebar
from components.theme import get_css
from database.db import init_db
from pages import (
    dashboard,
    excel_import,
    idle_balance,
    interest_validation,
    recount_management,
    reports,
    round_tripping,
    settings,
    signatory_verification,
)

PAGE_MAP = {
    "Dashboard": dashboard,
    "Recount Management": recount_management,
    "Fund Round-Tripping Detection": round_tripping,
    "Interest & Bank Charge Validation": interest_validation,
    "Idle Balance Monitoring": idle_balance,
    "Signatory Verification": signatory_verification,
    "Excel Import Center": excel_import,
    "Reports": reports,
    "Settings": settings,
}


def init_session():
    defaults = {
        "role": "Auditor",
        "username": "Auditor User",
        "dark_mode": True,
        "db_initialized": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def main():
    st.set_page_config(
        page_title="CAP AI - Recount Management Workspace",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session()

    if not st.session_state.get("db_initialized"):
        init_db()
        st.session_state["db_initialized"] = True

    dark_mode = st.session_state.get("dark_mode", True)
    st.markdown(get_css(dark_mode), unsafe_allow_html=True)

    selected = render_sidebar()
    page_module = PAGE_MAP.get(selected, dashboard)
    page_module.render()


if __name__ == "__main__":
    main()
