import streamlit as st

from components.ai_insights import render_ai_insights_panel
from components.charts import (
    branch_risk_distribution,
    recount_progress_tracker,
    risk_heatmap,
    transaction_trend_chart,
)
from components.kpi_cards import page_header, render_kpi_grid
from database import crud


def render():
    page_header("Executive Dashboard", "Real-time audit intelligence overview")

    with st.spinner("Loading dashboard metrics..."):
        kpis = crud.get_dashboard_kpis()
        cases = crud.get_recount_cases()

    kpi_data = {
        "Total Accounts Reviewed": (kpis["total_accounts"], "+12 this month"),
        "Transactions Analyzed": (kpis["transactions_analyzed"], "+847 this week"),
        "Suspicious Transactions": (kpis["suspicious_transactions"], "Requires review"),
        "Idle Balances Found": (kpis["idle_balances"], "₹25L+ flagged"),
        "Interest Deviations": (kpis["interest_deviations"], "Variance detected"),
        "Unauthorized Approvals": (kpis["unauthorized_approvals"], "Escalated"),
        "Active Recount Cases": (kpis["active_recount_cases"], "In progress"),
        "Observer Assignments": (kpis["observer_assignments"], "Scheduled"),
    }
    render_kpi_grid(kpi_data)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(transaction_trend_chart(), use_container_width=True)
    with col2:
        st.plotly_chart(risk_heatmap(), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(branch_risk_distribution(), use_container_width=True)
    with col4:
        st.plotly_chart(recount_progress_tracker(cases), use_container_width=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    render_ai_insights_panel()
