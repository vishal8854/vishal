import pandas as pd
import streamlit as st

from components.kpi_cards import page_header
from database import crud
from utils.auth import can_access
from utils.data_profiling import normalize_columns, profile_dataframe


def _read_upload(uploaded) -> pd.DataFrame:
    if uploaded.name.endswith(".csv"):
        return normalize_columns(pd.read_csv(uploaded))
    return normalize_columns(pd.read_excel(uploaded, engine="openpyxl"))


def render():
    page_header("Excel Import Center", "Upload, preview, and profile audit data")

    if not can_access(st.session_state.get("role", "Auditor"), "import"):
        st.warning("Your role does not have access to this module.")
        return

    import_type = st.selectbox(
        "Data Type",
        ["Transactions", "Interest Validation", "Idle Accounts", "Signatories"],
    )

    idle_days = st.number_input("Idle threshold (days)", 30, 365, 60, key="idle_thresh_import")
    balance_thresh = st.number_input("Balance threshold (₹)", 10000, 10000000, 100000, key="bal_thresh_import")

    uploaded = st.file_uploader("Drag & drop or browse files", type=["xlsx", "csv"])

    if uploaded:
        df = _read_upload(uploaded)

        st.markdown("#### Data Preview")
        st.dataframe(df.head(20), use_container_width=True, hide_index=True)

        profile = profile_dataframe(df)
        st.markdown("#### Data Profiling")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows", profile["rows"])
        c2.metric("Columns", profile["columns"])
        c3.metric("Duplicates", profile["duplicates"])
        c4.metric("Outlier Columns", len(profile.get("outliers", {})))

        if profile.get("missing"):
            st.markdown("**Missing Values:**")
            st.json(profile["missing"])
        if profile.get("outliers"):
            st.markdown("**Outliers (IQR method):**")
            st.json(profile["outliers"])

        st.markdown("**Column Types:**")
        st.json(profile.get("dtypes", {}))

        user = st.session_state.get("username", "User")
        role = st.session_state.get("role", "Auditor")

        if st.button("✅ Import to Database", type="primary"):
            with st.spinner("Importing data..."):
                if import_type == "Transactions":
                    count = crud.bulk_insert_transactions(df, user, role)
                elif import_type == "Interest Validation":
                    count = crud.bulk_insert_interest(df, user, role)
                elif import_type == "Idle Accounts":
                    count = crud.bulk_insert_idle(df, idle_days, balance_thresh, user, role)
                else:
                    count = crud.bulk_insert_signatories(df, user, role)
                st.success(f"Successfully imported {count} records into {import_type}.")
