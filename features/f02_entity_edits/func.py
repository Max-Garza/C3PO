import sqlite3
from dataclasses import asdict
from shared.entities import *
import streamlit as st
from features.f01_entity_creation.func import get_id_by_field, check_entry_similarity, column_as_list
from datetime import datetime

def update_entity_row(
    conn: sqlite3.Connection,
    table_name: str,
    entity_id: int,
    entity
) -> None:
    # Convert entity's data class into a dictionary
    data = asdict(entity)
    if 'id' in data:
        data.pop('id')

    # Get data class keys as SQL columns (UPDATE syntax)
    set_clauses = ", ".join([f"{key} = ?" for key in data.keys()])

    # Associate set_clauses with the entity's ID
    values = tuple(data.values()) + (entity_id,)

    # Construct the UPDATE query
    query = f"UPDATE {table_name} SET {set_clauses} WHERE id = ?"

    # Execute query and commit the change
    conn.execute(query, values)
    conn.commit()

def safe_update(
    conn: sqlite3.Connection,
    table_name: str,
    entity_id: int,
    entity,
    checks: list,
    override: bool
) -> list:
    # Grab list of warning / block check results
    issues = [c for c in checks if c != "PASS"]

    # If update is blocked, do nothing - just return the issues list for later printing
    if any("BLOCKED" in i for i in issues):
        return issues
    
    # If update has warning checks and the user hasn't overridden, return the issues list for later printing
    if issues and not override:
        return issues
    
    # If update passes or user has overriden the warning, try updating the entity
    try:
        update_entity_row(conn, table_name, entity_id, entity)
        return ["SUCCESS"]
    except Exception as e:
        return [f"DATABASE ERROR: {str(e)}"]

def edit_management_level(
    conn: sqlite3.Connection,
    target_name: str,
    new_name: str,
    new_seniority_score: int,
    override: bool=False
) -> list:
    if not (1 <= new_seniority_score <= 5):
        raise ValueError("Seniority score must be between 1 and 5")

    table_name = 'management_level'
    target_id = get_id_by_field(conn, table_name, 'name', target_name)
    row = ManagementLevel(
        id=target_id,
        name=new_name,
        seniority_score=new_seniority_score
    )

    if new_name != target_name:
        checks = [
            check_entry_similarity(conn, row, "name", new_name)
        ]
    else:
        checks=["PASS"]

    return safe_update(conn, table_name, target_id, row, checks, override)

def edit_team(
    conn: sqlite3.Connection,
    target_name: str,
    new_name: str,
    new_description: str,
    override: bool=False
) -> list:
    table_name = 'team'
    target_id = get_id_by_field(conn, table_name, 'name', target_name)
    row = Team(
        id=target_id,
        name=new_name,
        description = new_description
    )

    if new_name != target_name:
        checks = [
            check_entry_similarity(conn, row, "name", new_name)
        ]
    else:
        checks=["PASS"]

    return safe_update(conn, table_name, target_id, row, checks, override)

def edit_portfolio(
    conn: sqlite3.Connection,
    target_name: str,
    new_name: str,
    new_description: str,
    override: bool=False
) -> list:
    table_name = 'portfolio'
    target_id = get_id_by_field(conn, table_name, 'name', target_name)
    row = Portfolio(
        id=target_id,
        name=new_name,
        description=new_description
    )
    
    if new_name != target_name:
        checks = [
            check_entry_similarity(conn, row, "name", new_name)
        ]
    else:
        checks=["PASS"]

    return safe_update(conn, table_name, target_id, row, checks, override)

def edit_status(
    conn: sqlite3.Connection,
    target_name: str,
    new_name: str,
    override: bool=False
) -> list:
    table_name = 'status'
    target_id = get_id_by_field(conn, table_name, 'name', target_name)
    row = Status(
        id=target_id,
        name=new_name
    )

    checks = [
        check_entry_similarity(conn, row, "name", new_name)
    ]

    return safe_update(conn, table_name, target_id, row, checks, override)

def edit_request_type(
    conn: sqlite3.Connection,
    target_name: str,
    new_name: str,
    override: bool=False
) -> list:
    table_name = 'request_type'
    target_id = get_id_by_field(conn, table_name, 'name', target_name)
    row = RequestType(
        id=target_id,
        name=new_name
    )

    checks = [
        check_entry_similarity(conn, row, "name", new_name)
    ]

    return safe_update(conn, table_name, target_id, row, checks, override)

def edit_duration_unit(
    conn: sqlite3.Connection,
    target_name: str,
    new_name: str,
    override: bool=False
) -> list:
    table_name = 'duration_units'
    target_id = get_id_by_field(conn, table_name, 'name', target_name)
    row = DurationUnits(
        id=target_id,
        name=new_name
    )

    checks = [
        check_entry_similarity(conn, row, "name", new_name)
    ]

    return safe_update(conn, table_name, target_id, row, checks, override)

def edit_user(
    conn: sqlite3.Connection,
    target_name: str,
    new_name: str,
    new_management_level_name: str,
    new_team_name: str,
    new_active_status: bool,
    override: bool=False
) -> list:
    table_name = 'user'
    cursor = conn.execute(f"SELECT id, username FROM {table_name} WHERE name = ?", (target_name,))
    id_username = cursor.fetchone()
    target_id, username = id_username
    new_management_level_id = get_id_by_field(conn, 'management_level', 'name', new_management_level_name)
    new_team_id = get_id_by_field(conn, 'team', 'name', new_team_name)
    row = User(
        id=target_id,
        management_level_id=new_management_level_id,
        team_id=new_team_id,
        name=new_name,
        username=username,
        active_status=new_active_status
    )

    checks = ["PASS"]

    return safe_update(conn, table_name, target_id, row, checks, override)

def edit_ticket(
    conn: sqlite3.Connection,
    target_name: str,
    new_requester_name: str,
    new_project_name: Optional[str],
    new_assignee_name: Optional[str],
    new_request_type_name: str,
    new_name: str,
    new_description: str,
    new_due_date: Optional[date],
    new_start_date: Optional[date],
    new_end_date: Optional[date],
    new_estimated_duration_time: Optional[int],
    new_estimated_duration_unit_name: Optional[str],
    override: bool=False
) -> list:
    checks = ["PASS"]

    missing = []
    if not new_project_name: missing.append("Project")
    if not new_due_date: missing.append("Due Date")
    
    if missing:
        msg = ", ".join(missing)
        checks.append(f"WARNING: No {msg} provided. This will hide or de-prioritize your ticket. Proceed anyway?")
    
    table_name = 'ticket'
    target_id = get_id_by_field(conn, table_name, 'name', target_name)
    row = Ticket(
        id=target_id,
        requester_id=get_id_by_field(conn, 'user', 'name', new_requester_name),
        project_id=get_id_by_field(conn, 'project', 'name', new_project_name) if new_project_name else None,
        assignee_id=get_id_by_field(conn, 'user', 'name', new_assignee_name) if new_assignee_name else None,
        request_type_id=get_id_by_field(conn, 'request_type', 'name', new_request_type_name),
        name=new_name,
        description=new_description,
        due_date=new_due_date.isoformat() if new_due_date else None,
        start_date=new_start_date.isoformat() if new_start_date else None,
        end_date=new_end_date.isoformat() if new_end_date else None,
        estimated_duration_time=new_estimated_duration_time if new_estimated_duration_time else None,
        estimated_duration_units=get_id_by_field(conn, 'duration_units', 'name', new_estimated_duration_unit_name) if new_estimated_duration_unit_name else None
    )

    return safe_update(conn, table_name, target_id, row, checks, override)

def edit_project(
    conn: sqlite3.Connection,
    target_name: str,
    new_product_name: Optional[str],
    new_manager_name: Optional[str],
    new_name: str,
    new_description: str,
    override: bool=False
) -> list:
    checks = ["PASS"]

    missing = []
    if not new_product_name: missing.append("Product")
    if not new_manager_name: missing.append("Manager")

    if missing:
        msg = ", ".join(missing)
        checks.append(f"WARNING: No {msg} provided. This will hide or de-prioritize your project. Proceed anyway?")

    table_name = 'project'
    target_id = get_id_by_field(conn, table_name, 'name', target_name)
    row = Project(
        id=target_id,
        product_id=get_id_by_field(conn, 'product', 'name', new_product_name) if new_product_name else None,
        manager_id=get_id_by_field(conn, 'user', 'name', new_manager_name) if new_manager_name else None,
        name=new_name,
        description=new_description
    )

    if new_name != target_name:
        checks.append(check_entry_similarity(conn, row, "name", new_name))

    return safe_update(conn, table_name, target_id, row, checks, override)

def edit_product(
    conn: sqlite3.Connection,
    target_name: str,
    new_portfolio_name: Optional[str],
    new_manager_name: Optional[str],
    new_name: str,
    new_description: str,
    override: bool=False
) -> list:
    checks = ["PASS"]

    missing = []
    if not new_portfolio_name: missing.append("Portfolio")
    if not new_manager_name: missing.append("Manager")

    if missing:
        msg = ", ".join(missing)
        checks.append(f"WARNING: No {msg} provided. This will hide or de-prioritize your product. Proceed anyway?")

    table_name='product'
    target_id = get_id_by_field(conn, table_name, 'name', target_name)
    row = Product(
        id=target_id,
        portfolio_id=get_id_by_field(conn, 'portfolio', 'name', new_portfolio_name) if new_portfolio_name else None,
        manager_id=get_id_by_field(conn,'user', 'name', new_manager_name) if new_manager_name else None,
        name=new_name,
        description=new_description
    )

    if new_name != target_name:
        checks.append(check_entry_similarity(conn, row, "name", new_name))

    return safe_update(conn, table_name, target_id, row, checks, override)

def get_row_dict(conn: sqlite3.Connection, table: str, name: str) -> dict:
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(f"SELECT * FROM {table} WHERE name = ?", (name,))
    row = cursor.fetchone()
    return dict(row) if row else {}

def get_name_by_id(conn: sqlite3.Connection, table: str, row_id: int) -> str:
    if row_id is None: return None
    cursor = conn.execute(f"SELECT name FROM {table} WHERE id = ?", (row_id,))
    res = cursor.fetchone()
    return res[0] if res else None

@st.dialog("Edit Existing Entity")
def edit_entity_modal(conn: sqlite3.Connection) -> None:
    # 1. Select the Type
    entity_type = st.selectbox(
        "What kind of entity are you editing?",
        ["Portfolio", "Product", "Project", "Ticket", "User", "Team", "Request Type", "Completion Status", "Seniority Level", "Time Duration Unit"]
    )

    table_map = {
        "Portfolio": "portfolio", "Product": "product", "Project": "project",
        "Ticket": "ticket", "User": "user", "Team": "team",
        "Request Type": "request_type", "Completion Status": "status",
        "Seniority Level": "management_level", "Time Duration Unit": "duration_units"
    }
    table = table_map[entity_type]

    # 2. Select the specific Record
    names = column_as_list(conn, table, "name")
    target_name = st.selectbox(f"Select the {entity_type} to modify", names)

    if not target_name:
        st.info(f"No {entity_type} entries found to edit.")
        return

    # 3. Fetch current data
    vals = get_row_dict(conn, table, target_name)
    st.divider()

    if "edit_override" not in st.session_state:
        st.session_state.edit_override = False

    # 4. The Form
    with st.form("edit_entity_form", clear_on_submit=False):
        f = {}

        def get_idx(options, current_val):
            try: return options.index(current_val)
            except: return 0
        
        def parse_date(d_str):
            return datetime.strptime(d_str, "%Y-%m-%d").date() if d_str else None

        if entity_type == "Portfolio":
            f["name"] = st.text_input("Portfolio Name", value=vals.get("name"))
            f["description"] = st.text_area("Description", value=vals.get("description"))

        elif entity_type == "Product":
            portfolios = column_as_list(conn, "portfolio", "name")
            managers = column_as_list(conn, "user", "name")
            curr_port = get_name_by_id(conn, "portfolio", vals.get("portfolio_id"))
            curr_mgr = get_name_by_id(conn, "user", vals.get("manager_id"))
            f["name"] = st.text_input("Product Name", value=vals.get("name"))
            f["description"] = st.text_area("Description", value=vals.get("description"))
            f["portfolio_name"] = st.selectbox("Portfolio", portfolios, index=get_idx(portfolios, curr_port))
            f["manager_name"] = st.selectbox("Manager", managers, index=get_idx(managers, curr_mgr))

        elif entity_type == "Project":
            products = column_as_list(conn, "product", "name")
            managers = column_as_list(conn, "user", "name")
            curr_prod = get_name_by_id(conn, "product", vals.get("product_id"))
            curr_mgr = get_name_by_id(conn, "user", vals.get("manager_id"))
            f["name"] = st.text_input("Project Name", value=vals.get("name"))
            f["description"] = st.text_area("Description", value=vals.get("description"))
            f["product_name"] = st.selectbox("Associated Product", products, index=get_idx(products, curr_prod))
            f["manager_name"] = st.selectbox("Project Manager", managers, index=get_idx(managers, curr_mgr))

        elif entity_type == "Ticket":
            users = column_as_list(conn, "user", "name")
            projects = column_as_list(conn, "project", "name")
            req_types = column_as_list(conn, "request_type", "name")
            dur_units = column_as_list(conn, "duration_units", "name")
            
            f["name"] = st.text_input("Ticket Name", value=vals.get("name"))
            f["description"] = st.text_area("Description", value=vals.get("description"))
            f["request_type_name"] = st.selectbox("Request Type", req_types, index=get_idx(req_types, get_name_by_id(conn, "request_type", vals.get("request_type_id"))))
            f["requester_name"] = st.selectbox("Requester", users, index=get_idx(users, get_name_by_id(conn, "user", vals.get("requester_id"))))
            f["assignee_name"] = st.selectbox("Assignee", users, index=get_idx(users, get_name_by_id(conn, "user", vals.get("assignee_id"))))
            f["project_name"] = st.selectbox("Project", projects, index=get_idx(projects, get_name_by_id(conn, "project", vals.get("project_id"))))
            f["due_date"] = st.date_input("Due Date", value=parse_date(vals.get("due_date")))
            f["start_date"] = st.date_input("Start Date", value=parse_date(vals.get("start_date")))
            f["end_date"] = st.date_input("End Date", value=parse_date(vals.get("end_date")))
            f["est_time"] = st.number_input("Est. Time", value=float(vals.get("estimated_duration_time") or 0))
            f["est_unit"] = st.selectbox("Unit", dur_units, index=get_idx(dur_units, get_name_by_id(conn, "duration_units", vals.get("estimated_duration_units"))))

        elif entity_type == "User":
            teams = column_as_list(conn, "team", "name")
            levels = column_as_list(conn, "management_level", "name")
            f["name"] = st.text_input("User Name", value=vals.get("name"))
            f["team_name"] = st.selectbox("Team", teams, index=get_idx(teams, get_name_by_id(conn, "team", vals.get("team_id"))))
            f["management_level_name"] = st.selectbox("Level", levels, index=get_idx(levels, get_name_by_id(conn, "management_level", vals.get("management_level_id"))))
            f["active_status"] = st.checkbox("Active", value=bool(vals.get("active_status")))

        elif entity_type == "Team":
            f["name"] = st.text_input("Team Name", value=vals.get("name"))
            f["description"] = st.text_area("Description", value=vals.get("description"))

        elif entity_type == "Request Type":
            f["name"] = st.text_input("Request Type", value=vals.get("name"))

        elif entity_type == "Completion Status":
            f["name"] = st.text_input("Status Name", value=vals.get("name"))

        elif entity_type == "Seniority Level":
            f["name"] = st.text_input("Level Name", value=vals.get("name"))
            f["score"] = st.selectbox("Score", [1,2,3,4,5], index=get_idx([1,2,3,4,5], vals.get("seniority_score")))

        elif entity_type == "Time Duration Unit":
            f["name"] = st.text_input("Unit Name", value=vals.get("name"))

        submitted = st.form_submit_button("Save Changes")

        if submitted:
            override = st.session_state.edit_override
            res = ["BLOCKED: No logic for this type."]

            if entity_type == "Portfolio":
                res = edit_portfolio(conn, target_name, f["name"], f["description"], override)
            elif entity_type == "Product":
                res = edit_product(conn, target_name, f["portfolio_name"], f["manager_name"], f["name"], f["description"], override)
            elif entity_type == "Project":
                res = edit_project(conn, target_name, f["product_name"], f["manager_name"], f["name"], f["description"], override)
            elif entity_type == "Ticket":
                res = edit_ticket(conn, target_name, f["requester_name"], f["project_name"], f["assignee_name"], f["request_type_name"], f["name"], f["description"], f["due_date"], f["start_date"], f["end_date"], f["est_time"], f["est_unit"], override)
            elif entity_type == "User":
                res = edit_user(conn, target_name, f["name"], f["management_level_name"], f["team_name"], f["active_status"], override)
            elif entity_type == "Team":
                res = edit_team(conn, target_name, f["name"], f["description"], override)
            elif entity_type == "Request Type":
                res = edit_request_type(conn, target_name, f["name"], override)
            elif entity_type == "Completion Status":
                res = edit_status(conn, target_name, f["name"], override)
            elif entity_type == "Seniority Level":
                res = edit_management_level(conn, target_name, f["name"], f["score"], override)
            elif entity_type == "Time Duration Unit":
                res = edit_duration_unit(conn, target_name, f["name"], override)

            if any("BLOCKED" in msg for msg in res):
                for msg in res: st.error(msg)
                st.session_state.edit_override = False
            elif any("WARNING" in msg for msg in res):
                for msg in res: st.warning(msg)
                st.session_state.edit_override = True
            elif "SUCCESS" in res:
                st.success(f"{entity_type} updated!")
                st.session_state.edit_override = False
                st.rerun()