import sqlite3
from dataclasses import asdict
from shared.schema import camel_to_snake
from shared.entities import *
from difflib import SequenceMatcher
import re
import streamlit as st

def norm_text(text: str) -> str:
    return text.lower().strip()

def calculate_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def validate_unique_name(conn: sqlite3.Connection, table: str, column: str, new_value: str) -> dict:
    cursor = conn.execute(f"SELECT {column} FROM {table}")
    current = [row[0] for row in cursor.fetchall()]

    if not current:
        return {
        "match": None,
        "score": 0.0,
        "input_val": new_value
    }

    norm_new_value = norm_text(new_value)

    similarities = {val: calculate_similarity(norm_new_value, norm_text(val)) for val in current}

    best_match = max(similarities, key=similarities.get)
    
    return {
        "match": best_match,
        "score": similarities[best_match],
        "input_val": new_value
    }
    
def similarity_check(conn: sqlite3.Connection, table: str, column: str, new_value: str) -> str:
    similarity_dict = validate_unique_name(conn, table, column, new_value)
    score = similarity_dict["score"]
    match = similarity_dict["match"]
    input_val = similarity_dict["input_val"]

    if score >= 0.91:
        return f'BLOCKED: "{input_val}" is too similar to existing {table} value "{match}"'
    elif score >= 0.75:
        return f'WARNING: "{input_val}" is similar to existing {table} value "{match}". Proceed anyway?'
    else:
        return "PASS"

def insert_entity_row(conn: sqlite3.Connection, table_name: str, entity) -> None:
    data = asdict(entity)

    if 'id' in data:
        data.pop('id')
    
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    values = tuple(data.values())

    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    conn.execute(query, values)
    conn.commit()

def check_entry_similarity(conn: sqlite3.Connection, entity, column: str, new_value: str) -> tuple:
    table = camel_to_snake(type(entity))
    return similarity_check(conn, table, column, new_value)

def safe_insert(conn: sqlite3.Connection, table_name: str, entity,  checks: list, override: bool) -> list:
    issues = [c for c in checks if c != "PASS"]

    if any("BLOCKED" in i for i in issues):
        return issues

    if issues and not override:
        return issues

    try:
        insert_entity_row(conn, table_name, entity)
        return ["SUCCESS"]
    except Exception as e:
        return [f"DATABASE ERROR: {str(e)}"]
    
def get_id_by_field(conn: sqlite3.Connection, table_name: str, field: str, value) -> int:
    query = f"SELECT id FROM {table_name} WHERE {field} = ?"
    cursor = conn.execute(query, (value,))
    result = cursor.fetchone()

    if not result:
        raise ValueError(f"Lookup Failed: Could not find '{value}' in table '{table_name}'. Did it fail to insert?")

    return result[0]

def add_management_level(conn: sqlite3.Connection, name: str, seniority_score: int, override: bool=False) -> list:
    if not (1 <= seniority_score <= 5):
        raise ValueError("Seniority score must be between 1 and 5")
    
    table_name = camel_to_snake(ManagementLevel)
    
    row = ManagementLevel(
        id=None,
        name=name,
        seniority_score=seniority_score
    )

    checks = [
        check_entry_similarity(conn, row, "name", name)
    ]
    
    return safe_insert(conn, table_name, row, checks, override)

def add_team(conn: sqlite3.Connection, name: str, description: str, override: bool=False) -> list:
    table_name = camel_to_snake(Team)
    
    row = Team(
        id=None,
        name=name,
        description=description
    )

    checks = [
        check_entry_similarity(conn, row, "name", name)
    ]
    
    return safe_insert(conn, table_name, row, checks, override)

def add_portfolio(conn: sqlite3.Connection, name: str, description: str, override: bool=False) -> list:
    table_name = camel_to_snake(Portfolio)
    
    row = Portfolio(
        id=None,
        name=name,
        description=description
    )

    checks = [
        check_entry_similarity(conn, row, "name", name)
    ]
    
    return safe_insert(conn, table_name, row, checks, override)

def add_status(conn: sqlite3.Connection, name: str, override: bool=False) -> list:
    table_name = camel_to_snake(Status)

    row = Status(
        id=None,
        name=name
    )

    checks = [
        check_entry_similarity(conn, row, "name", name)
    ]

    return safe_insert(conn, table_name, row, checks, override)

def add_request_type(conn: sqlite3.Connection, name: str, override: bool=False) -> list:
    table_name = camel_to_snake(RequestType)

    row = RequestType(
        id=None,
        name=name
    )

    checks = [
        check_entry_similarity(conn, row, "name", name)
    ]

    return safe_insert(conn, table_name, row, checks, override)

def add_duration_unit(conn: sqlite3.Connection, name: str, override: bool=False) -> list:
    table_name = camel_to_snake(DurationUnits)

    row = DurationUnits(
        id=None,
        name=name
    )

    checks = [
        check_entry_similarity(conn, row, "name", name)
    ]

    return safe_insert(conn, table_name, row, checks, override)

def generate_username(conn: sqlite3.Connection, name: str) -> str:
    parts = norm_text(name).split()

    if len(parts) > 1:
        initials = "".join([p[0] for p in parts[:-1]])
        last_name = parts[-1]
        base = initials + last_name
    else:
        base = parts[0]

    username = re.sub(r'[^a-z0-9]', '', base)

    counter = 1
    
    while True:
        # Check if username exists
        query = "SELECT 1 FROM user WHERE username = ?"
        if not conn.execute(query, (username,)).fetchone():
            return username
        
        # If exists, append number and try again
        username = f"{base}{counter}"
        counter += 1

def add_user(
    conn: sqlite3.Connection,
    name: str,
    management_level_name: str,
    team_name: str,
    active_status: bool=True,
    override: bool=False
) -> list:
    management_level_id = get_id_by_field(conn, "management_level", "name", management_level_name)
    team_id = get_id_by_field(conn, "team", "name", team_name)
    
    username = generate_username(conn, name)

    table_name = camel_to_snake(User)

    row = User(
        id=None,
        management_level_id=management_level_id,
        team_id=team_id,
        name=name,
        username=username,
        active_status=active_status
    )

    checks = ["PASS"]

    return safe_insert(conn, table_name, row, checks, override)

def add_ticket(
    conn: sqlite3.Connection,
    requester_name: str,
    project_name: Optional[str],
    assignee_name: Optional[str],
    request_type_name: str,
    name: str,
    description: str,
    due_date: Optional[date],
    override: bool=False
) -> list:
    
    checks = ["PASS"]

    missing = []
    if not project_name: missing.append("Project")
    if not due_date: missing.append("Due Date")
    
    if missing:
        msg = ", ".join(missing)
        checks.append(f"WARNING: No {msg} provided. This will hide or de-prioritize your ticket. Proceed anyway?")

    table_name = camel_to_snake(Ticket)

    row = Ticket(
        id=None,
        requester_id=get_id_by_field(conn, "user", "name", requester_name),
        project_id=get_id_by_field(conn, "project", "name", project_name) if project_name else None,
        assignee_id=get_id_by_field(conn, "user", "name", assignee_name) if assignee_name else None,
        request_type_id=get_id_by_field(conn, "request_type", "name", request_type_name),
        name=name,
        description=description,
        due_date=due_date.isoformat() if due_date else None,
        start_date=None,
        end_date=None,
        estimated_duration_time=None,
        estimated_duration_units=None,
        status_id=1
    )

    return safe_insert(conn, table_name, row, checks, override)

def add_project(
    conn: sqlite3.Connection,
    product_name: Optional[str],
    manager_name: Optional[str],
    name: str,
    description: str,
    override: bool=False
) -> list:
    
    checks = ["PASS"]

    missing = []
    if not product_name: missing.append("Product")
    if not manager_name: missing.append("Manager")

    if missing:
        msg = ", ".join(missing)
        checks.append(f"WARNING: No {msg} provided. This will hide or de-prioritize your project. Proceed anyway?")
    
    table_name = camel_to_snake(Project)

    row = Project(
        id=None,
        product_id=get_id_by_field(conn, "product", "name", product_name) if product_name else None,
        manager_id=get_id_by_field(conn, "user", "name", manager_name) if manager_name else None,
        name=name,
        description=description
    )

    checks.append(check_entry_similarity(conn, row, "name", name))

    return safe_insert(conn, table_name, row, checks, override)

def add_product(
    conn: sqlite3.Connection,
    portfolio_name: Optional[str],
    manager_name: Optional[str],
    name: str,
    description: str,
    override: bool=False
) -> list:
    
    checks = ["PASS"]

    missing = []
    if not portfolio_name: missing.append("Portfolio")
    if not manager_name: missing.append("Manager")

    if missing:
        msg = ", ".join(missing)
        checks.append(f"WARNING: No {msg} provided. This will hide or de-prioritize your product. Proceed anyway?")
    
    table_name = camel_to_snake(Product)

    row = Product(
        id=None,
        portfolio_id=get_id_by_field(conn, "portfolio", "name", portfolio_name) if portfolio_name else None,
        manager_id=get_id_by_field(conn, "user", "name", manager_name) if manager_name else None,
        name=name,
        description=description
    )

    checks.append(check_entry_similarity(conn, row, "name", name))

    return safe_insert(conn, table_name, row, checks, override)

def column_as_list(conn: sqlite3.Connection, table: str, column: str) -> list:
    query = f"SELECT DISTINCT {column} FROM {table}"
    cursor = conn.execute(query)
    values = [row[0] for row in cursor.fetchall()]
    return sorted(values)

@st.dialog("Create New Entity")
def create_entity_modal(conn: sqlite3.Connection) -> None:
    entity_type = st.selectbox(
        "What would you like to create?",
        ["Portfolio", "Product", "Project", "Ticket", "User", "Team", "Request Type", "Completion Status", "Seniority Level", "Time Duration Unit"]
    )

    st.divider()

    if "override_active" not in st.session_state:
        st.session_state.override_active = False

    with st.form("entity_form", clear_on_submit=False):
        if entity_type == "Portfolio":
            name = st.text_input("Portfolio Name")
            description = st.text_area("Description")
        
        elif entity_type == "Product":
            name = st.text_input("Product Name")
            description = st.text_area("Description")
            portfolio_name = st.selectbox("Portfolio", column_as_list(conn, "portfolio", "name"))
            manager_name = st.selectbox("Manager", column_as_list(conn, "user", "name"))
        
        elif entity_type == "Project":
            name = st.text_input("Project Name")
            description = st.text_area("Description")
            product_name = st.selectbox("Associated Product", column_as_list(conn, "product", "name"))
        
        elif entity_type == "Ticket":
            name = st.text_input("Ticket Name")
            request_type_name = st.selectbox("Request Type", column_as_list(conn, "request_type", "name"))
            description = st.text_area("Description")
            requester_name = st.selectbox("Requester Name", column_as_list(conn, "user", "name"))
            assignee_name = st.selectbox("Assignee Name", column_as_list(conn, "user", "name"))
            due_date = st.date_input("Due Date", value=None)
            project_name = st.selectbox("Associated Project", column_as_list(conn, "project", "name"))
        
        elif entity_type == "User":
            name = st.text_input("User Name")
            team_name = st.selectbox("Team Name", column_as_list(conn, "team", "name"))
            management_level_name = st.selectbox("Seniority Level", column_as_list(conn, "management_level", "name"))
        
        elif entity_type == "Team":
            name = st.text_input("Team Name")
            description = st.text_area("Description")
        
        elif entity_type == "resuest Type":
            name = st.text_input("resuest Type Name")
        
        elif entity_type == "Completion Status":
            name = st.text_input("Completion Status Name")

        elif entity_type == "Seniority Level":
            name = st.text_input("Seniority Level Name")
            seniority_score = st.selectbox("Seniority Score (5 = most senior)", [1,2,3,4,5])
        
        elif entity_type == "Time Duration Units":
            name = st.text_input("Time Duration Unit Name")
        
        else:
            raise ValueError("Invalid entity type. Check code")
        
        if entity_type == "Portfolio":
            res = add_portfolio(conn, name, description)
        
        elif entity_type == "Product":
            res = add_product(conn, portfolio_name, manager_name, name, description)
        
        elif entity_type == "Project":
            res = add_project(conn, product_name, manager_name, name, description)
        
        elif entity_type == "Ticket":
            res = add_ticket(conn, requester_name, project_name, assignee_name, request_type_name, name, description, due_date)
        
        elif entity_type == "User":
            res = add_user(conn, name, management_level_name, team_name)
        
        elif entity_type == "Team":
            res = add_team(conn, name, description)
        
        elif entity_type == "resuest Type":
            res = add_request_type(conn, name)
        
        elif entity_type == "Completion Status":
            res = add_status(conn, name)

        elif entity_type == "Seniority Level":
            res = add_management_level(conn, name, seniority_score)
        
        elif entity_type == "Time Duration Units":
            res = add_duration_unit(conn, name)
        
        submitted = st.form_submit_button("Submit")

        if submitted:
            try:
                if any("BLOCKED" in msg for msg in res):
                    for msg in res: st.warning(msg)
                    st.session_state.override_active = False
                
                elif any("WARNING" in msg for msg in res):
                    for msg in res: st.warning(msg)
                    st.session_state.override_active = True
                
                elif "SUCCESS" in res:
                    st.success(f"{entity_type} created successfully")
                    st.session_state.override_active = False
                    st.rerun()
            except Exception as e:
                st.errot(f"An error occurred: {e}")