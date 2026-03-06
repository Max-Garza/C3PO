from shared.schema import create_db_pipeline
from shared.sample import sample_entities
from features.f01_entity_creation.func import create_entity_modal
from features.f02_entity_edits.func import edit_entity_modal
import streamlit as st
import pandas as pd

conn = create_db_pipeline()

counts = []
for i in ["user", "ticket"]:
    counts.append(conn.execute(f"SELECT COUNT(*) FROM {i}").fetchone()[0])

if max(counts) == 0:
    sample_entities(conn)

st.set_page_config(layout="wide", page_title="C3PO")

if "view" not in st.session_state:
    st.session_state.view = "Dashboard"
if "selected_entity" not in st.session_state:
    st.session_state.selected_entity = None

with st.sidebar:
    st.title("C3PO")
    st.divider()

    nav = st.radio(
        "Navigation",
        [
            "Portfolios",
            "Products",
            "Projects",
            "Tickets",
            "Users",
            "Admin"
        ]
    )

    st.divider()

    if st.button("Create New Entity", use_container_width=True):
        create_entity_modal(conn)
    
    if st.button("Edit Existing Entity", use_container_width=True):
        edit_entity_modal(conn)

if nav == "Portfolios":

    tab1, tab2 = st.tabs(["Overview", "Product Health"])

    with tab1:
        st.header("useful header")

        col1, col2 = st.columns(2)
        col1.metric("metric1", "x")
        col2.metric("metric2", "x")

        st.subheader("plot1")
        st.info("Plotly Chart will render here.") # Replace with plotly visual in future
    
    with tab2:
        st.header("useful header")

        col1, col2 = st.columns(2)
        col1.metric("metric1", "x")
        col2.metric("metric2", "x")

        st.subheader("plot1")
        st.info("Plotly Chart will render here.") # Replace with plotly visual in future

if nav == "Products":

    tab1, tab2 = st.tabs(["Overview", "Project Health"])

    with tab1:
        st.header("useful header")

        col1, col2 = st.columns(2)
        col1.metric("metric1", "x")
        col2.metric("metric2", "x")

        st.subheader("plot1")
        st.info("Plotly Chart will render here.") # Replace with plotly visual in future
    
    with tab2:
        st.header("useful header")

        col1, col2 = st.columns(2)
        col1.metric("metric1", "x")
        col2.metric("metric2", "x")

        st.subheader("plot1")
        st.info("Plotly Chart will render here.") # Replace with plotly visual in future

if nav == "Projects":

    tab1, tab2, tab3 = st.tabs(["Overview", "Timeline", "Ticket Health"])

    with tab1:
        st.header("useful header")

        col1, col2 = st.columns(2)
        col1.metric("metric1", "x")
        col2.metric("metric2", "x")

        st.subheader("plot1")
        st.info("Plotly Chart will render here.") # Replace with plotly visual in future
    
    with tab2:
        st.header("useful header")

        col1, col2 = st.columns(2)
        col1.metric("metric1", "x")
        col2.metric("metric2", "x")

        st.subheader("plot1")
        st.info("Plotly Chart will render here.") # Replace with plotly visual in future

    with tab3:
        st.header("useful header")

        col1, col2 = st.columns(2)
        col1.metric("metric1", "x")
        col2.metric("metric2", "x")

        st.subheader("plot1")
        st.info("Plotly Chart will render here.") # Replace with plotly visual in future

if nav == "Tickets":
    
    tab1, tab2 = st.tabs(["Overview", "Individual Tickets"])

    with tab1:
        st.header("useful header")

        col1, col2 = st.columns(2)
        col1.metric("metric1", "x")
        col2.metric("metric2", "x")

        st.subheader("plot1")
        st.info("Plotly Chart will render here.") # Replace with plotly visual in future
    
    with tab2:
        st.header("useful header")

        col1, col2 = st.columns(2)
        col1.metric("metric1", "x")
        col2.metric("metric2", "x")

        st.subheader("plot1")
        st.info("Plotly Chart will render here.") # Replace with plotly visual in future

if nav == "Users":

    tab1, tab2 = st.tabs(["Overview", "Single-User"])

    with tab1:
        st.header("useful header")

        col1, col2 = st.columns(2)
        col1.metric("metric1", "x")
        col2.metric("metric2", "x")

        st.subheader("plot1")
        st.info("Plotly Chart will render here.") # Replace with plotly visual in future
    
    with tab2:
        st.header("useful header")

        col1, col2 = st.columns(2)
        col1.metric("metric1", "x")
        col2.metric("metric2", "x")

        st.subheader("plot1")
        st.info("Plotly Chart will render here.") # Replace with plotly visual in future

def admin_pull(conn, table):
    query = f"SELECT * FROM {table}"
    df = pd.read_sql_query(query, conn)
    st.dataframe(df, use_container_width=True)

if nav == "Admin":

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(["Portfolio", "Product", "Project", "Ticket", "User", "Team", "Request Type", "Completion Status", "Seniority Level", "Time Duration Unit"])

    with tab1:
        admin_pull(conn, "portfolio")

    with tab2:
        admin_pull(conn, "product")
    
    with tab3:
        admin_pull(conn, "project")
    
    with tab4:
        admin_pull(conn, "ticket")
    
    with tab5:
        admin_pull(conn, "user")
    
    with tab6:
        admin_pull(conn, "team")
    
    with tab7:
        admin_pull(conn, "request_type")
    
    with tab8:
        admin_pull(conn, "status")
    
    with tab9:
        admin_pull(conn, "management_level")
    
    with tab10:
        admin_pull(conn, "duration_units")