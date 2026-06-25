from datetime import date
from pathlib import Path

import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

from components.filters import render_filters
from components.kpi_cards import page_header
from database import crud
from utils.auth import can_access

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "data" / "uploads"


def render():
    page_header("Recount Management Workspace", "Orchestrate recount logistics, observer scheduling & tally documentation")

    if not can_access(st.session_state.get("role", "Auditor"), "recount"):
        st.warning("Your role does not have access to this module.")
        return

    tab1, tab2, tab3 = st.tabs(["📋 Case Management", "📅 Observer Scheduling", "📄 Tally Documentation"])

    with tab1:
        _render_case_management()

    with tab2:
        _render_observer_scheduling()

    with tab3:
        _render_tally_docs()


def _render_case_management():
    cases = crud.get_recount_cases()
    branches = sorted(cases["branch"].unique().tolist()) if not cases.empty else []
    statuses = sorted(cases["status"].unique().tolist()) if not cases.empty else ["Open", "In Progress", "Scheduled", "Closed"]

    search, status, branch = render_filters(statuses, branches)
    global_search = st.session_state.get("global_search", "")
    if global_search:
        search = global_search

    cases = crud.get_recount_cases(search, status, branch)

    col1, col2 = st.columns([3, 1])
    with col2:
        with st.expander("➕ Create Case", expanded=False):
            with st.form("create_case"):
                case_id = st.text_input("Case ID", placeholder="RC-2026-006")
                branch_in = st.text_input("Branch")
                cashier = st.text_input("Cashier")
                amount = st.number_input("Amount (₹)", min_value=0.0, step=1000.0)
                if st.form_submit_button("Create Case"):
                    if crud.create_recount_case(case_id, branch_in, cashier, amount, st.session_state.get("username", "User"), st.session_state.get("role", "Auditor")):
                        st.success(f"Case {case_id} created!")
                        st.rerun()
                    else:
                        st.error("Case ID already exists.")

    if not cases.empty:
        display = cases[["case_id", "branch", "cashier", "amount", "status", "observer"]].copy()
        display.columns = ["Case ID", "Branch", "Cashier", "Amount", "Status", "Observer"]
        gb = GridOptionsBuilder.from_dataframe(display)
        gb.configure_pagination(paginationPageSize=10)
        gb.configure_default_column(filterable=True, sortable=True)
        AgGrid(display, gridOptions=gb.build(), height=300, theme="streamlit")

        st.markdown("#### Actions")
        ac1, ac2, ac3 = st.columns(3)
        case_ids = cases["case_id"].tolist()
        with ac1:
            sel_case = st.selectbox("Select Case", case_ids, key="action_case")
        with ac2:
            new_observer = st.text_input("Observer Name", key="assign_observer")
            if st.button("Assign Observer"):
                crud.assign_observer(sel_case, new_observer, st.session_state.get("username", "User"), st.session_state.get("role", "Auditor"))
                st.success(f"Observer assigned to {sel_case}")
                st.rerun()
        with ac3:
            new_status = st.selectbox("Update Status", ["Open", "In Progress", "Scheduled", "Closed"], key="update_status")
            if st.button("Update Status"):
                crud.update_recount_status(sel_case, new_status, st.session_state.get("username", "User"), st.session_state.get("role", "Auditor"))
                st.success(f"Status updated to {new_status}")
                st.rerun()
            if st.button("Close Case", type="primary"):
                crud.close_recount_case(sel_case, st.session_state.get("username", "User"), st.session_state.get("role", "Auditor"))
                st.success(f"Case {sel_case} closed.")
                st.rerun()
    else:
        st.info("No recount cases found. Create one to get started.")


def _render_observer_scheduling():
    schedule = crud.get_observer_schedule()

    with st.expander("➕ Schedule Observer"):
        with st.form("observer_form"):
            c1, c2 = st.columns(2)
            with c1:
                obs_name = st.text_input("Observer Name")
                branch = st.text_input("Branch")
            with c2:
                sched_date = st.date_input("Date", value=date.today())
                shift = st.selectbox("Shift", ["Morning", "Afternoon", "Evening"])
            remarks = st.text_area("Remarks")
            if st.form_submit_button("Add to Schedule"):
                crud.add_observer_schedule(obs_name, branch, str(sched_date), shift, remarks, st.session_state.get("username", "User"), st.session_state.get("role", "Auditor"))
                st.success("Observer scheduled!")
                st.rerun()

    if not schedule.empty:
        cal_df = schedule[["observer_name", "branch", "schedule_date", "shift", "remarks"]].copy()
        cal_df.columns = ["Observer Name", "Branch", "Date", "Shift", "Remarks"]
        st.dataframe(cal_df, use_container_width=True, hide_index=True)
    else:
        st.info("No observer schedules yet.")


def _render_tally_docs():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    cases = crud.get_recount_cases()
    case_ids = cases["case_id"].tolist() if not cases.empty else ["General"]

    case_sel = st.selectbox("Link to Case", case_ids)
    doc_type = st.selectbox("Document Type", ["Cash Tally Sheet", "Recount Sheet", "Supporting Documents"])

    uploaded = st.file_uploader("Upload Document", type=["pdf", "xlsx", "csv", "png", "jpg"])
    if uploaded:
        filepath = UPLOAD_DIR / uploaded.name
        filepath.write_bytes(uploaded.getvalue())
        crud.save_tally_document(case_sel, doc_type, uploaded.name, str(filepath), st.session_state.get("username", "User"), st.session_state.get("role", "Auditor"))
        st.success(f"Uploaded {uploaded.name}")

    docs = crud.get_tally_documents()
    if not docs.empty:
        st.dataframe(docs[["case_id", "doc_type", "filename", "uploaded_at"]], use_container_width=True, hide_index=True)
