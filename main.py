from shared.schema import create_db_pipeline
from shared.sample import sample_entities
import streamlit as st
import pandas as pd

conn = create_db_pipeline()
sample_entities(conn)

st.set_page_config(page_title="C3PO - Entity Viewer", layout="wide")

def get_data(conn, query) -> pd.DataFrame:
    return pd.read_sql_query(query, conn)

st.title("C3PO")
st.write("Sample portfolios, products, projects, and tickets")

tab1, tab2, tab3, tab4 = st.tabs(["Portfolios", "Products", "Projects", "Tickets"])

with tab1:
    st.header("Strategic Portfolios")
    df_portfolios = get_data(conn, "SELECT name, description FROM portfolio")
    st.dataframe(df_portfolios, use_container_width=True)

with tab2:
    st.header("Product Suite")
    query = """
        SELECT
            portfolio.name AS portfolio
            ,product.name
            ,product.description
        FROM product
        JOIN portfolio
            ON product.portfolio_id = portfolio.id
    """
    df_products = get_data(conn, query)
    st.dataframe(df_products, use_container_width=True)

with tab3:
    st.header("Active Projects")
    query = """
        SELECT
            product.name AS product
            ,user.name AS manager
            ,project.name
            ,project.description
        FROM project
        JOIN product
            ON project.product_id = product.id
        JOIN user 
            ON project.manager_id = user.id
    """
    df_projects = get_data(conn, query)
    st.dataframe(df_projects, use_container_width=True)

with tab4:
    st.header("Support and Task Tickets")
    query = """
        SELECT
            ticket.name AS ticket_title
            ,request_type.name AS request_type
            ,requester.name AS requester
            ,assignee.name AS assignee
            ,project.name AS project
            ,status.name AS status
            ,ticket.due_date
        FROM ticket
        LEFT JOIN user requester
            ON ticket.requester_id = requester.id
        LEFT JOIN user assignee
            ON ticket.assignee_id = assignee.id
        LEFT JOIN project
            ON ticket.project_id = project.id
        LEFT JOIN request_type
            ON ticket.request_type_id = request_type.id
        LEFT JOIN status
            ON ticket.status_id = status.id
    """
    df_tickets = get_data(conn, query)
    st.dataframe(df_tickets, use_container_width=True)