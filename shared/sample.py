import sqlite3
from datetime import date, timedelta
from features.f01_entity_creation.func import (
    add_management_level, add_team, add_portfolio, add_status,
    add_request_type, add_duration_unit, add_user, add_product,
    add_project, add_ticket
)
from datetime import date, timedelta

def sample_entities(conn: sqlite3.Connection) -> None:
    
    management_levels = [("Junior", 1), ("Senior", 2), ("Manager", 3), ("Director", 4), ("President", 5)]
    for name, score in management_levels:
        add_management_level(conn, name, score, override=True)
    
    teams = {
        "Operations": "Day-to-day process execution, optimization, and management",
        "H.R.": "Employee lifecycle management and benefits administration",
        "Marketing": "External marketing and advertising",
        "Finance": "Budget development, accounting, and forecasting",
        "I.T.": "Technical support/access and database management"
    }
    for name, description in teams.items():
        add_team(conn, name, description, override=True)
    
    portfolios = {
        "Internal Efficiency": "Reduce operational timelines and overhead via new tools and process improvement",
        "Market Growth": "Increase market share via effective marketing and new products",
        "Employee Experience": "Improve employee experience via reducing turnover and accelerating the hiring process"
    }
    for name, description in portfolios.items():
        add_portfolio(conn, name, description, override=True)

    statuses = ["Not Started", "In Progress", "Blocked", "Waiting for Requester Input", "Completed"]
    for name in statuses:
        add_status(conn, name)

    request_types = ["New Feature", "Bug Fix", "Analysis", "Infrastructure"]
    for name in request_types:
        add_request_type(conn, name, override=True)

    duration_units = ["Minutes", "Days", "Weeks", "Months", "Quarters", "Years"]
    for name in duration_units:
        add_duration_unit(conn, name, override=True)
    
    users = [
        ("Michael Scott", "President", "Operations"),
        ("James Halpert", "Director", "Operations"),
        ("Pamela Beesly", "Manager", "Operations"),
        ("Dwight Schrute", "Senior", "Operations"),
        ("Angela Martin", "Junior", "Operations"),
        ("Ben Wyatt", "President", "H.R."),
        ("Ron Swanson", "Director", "H.R."),
        ("Leslie Knope", "Manager", "H.R."),
        ("Donna Meagle", "Senior", "H.R."),
        ("April Ludgate", "Junior", "H.R."),
        ("Raymond Holt", "President", "Marketing"),
        ("Terry Jeffords", "Director", "Marketing"),
        ("Amy Santiago", "Manager", "Marketing"),
        ("Rosa Diaz", "Senior", "Marketing"),
        ("Jake Peralta", "Junior", "Marketing"),
        ("Jack Donaghy", "President", "Finance"),
        ("Kenneth Parcell", "Director", "Finance"),
        ("Liz Lemon", "Manager", "Finance"),
        ("Tracy Jordan", "Senior", "Finance"),
        ("Jeanna Maroney", "Junior", "Finance"),
        ("Denholm Reynholm", "President", "I.T."),
        ("Douglas Reynholm", "Director", "I.T."),
        ("Jen Barber", "Manager", "I.T."),
        ("Maurice Moss", "Senior", "I.T."),
        ("Roy Trenneman", "Junior", "I.T.")
    ]
    for name, management_level_name, team_name in users:
        add_user(conn, name, management_level_name, team_name, override=True)
    
    products = [
        ("Internal Efficiency", "Douglas Reynholm", "Company-wide A.I. Access", "Provide existing employees access to A.I. tools and usage training"),
        ("Internal Efficiency", "James Halpert", "Operations Process Improvement", "Investigate operations workflows and reduce delivery times"),
        ("Market Growth", "Terry Jeffords", "Product Discovery and Launch", "Perform market research and suggest new product to launch"),
        ("Market Growth", "Amy Santiago", "Market Demographic Expansion", "Expand marketing efforts to target new demographics"),
        ("Employee Experience", "Ron Swanson", "Turnover Reduction", "Identify reasons for turnover and develop countermeasures"),
        ("Employee Experience", "Leslie Knope", "Accelerate Hiring Process", "Find and close gaps that prolong hiring timelines")
    ]
    for portfolio_name, manager_name, name, description in products:
        add_product(conn, portfolio_name, manager_name, name, description, override=True)
    
    projects = [
        ("Company-wide A.I. Access", "Douglas Reynholm", "A.I. Tool Training", "Develop and distribute A.I. tool usage materials"),
        ("Company-wide A.I. Access", "Jen Barber", "A.I. Tool Access", "Give workers of all departments access to A.I. tools"),
        ("Operations Process Improvement", "James Halpert", "Enforce Process Improvements", "Implement process improvement steps across the department"),
        ("Operations Process Improvement", "Pamela Beesly", "Find Process Improvement Areas", "Analyze current processes and suggest improvements"),
        ("Product Discovery and Launch", "Terry Jeffords", "Product Suggestion", "Perform customer outreach, identity gaps in the market, and suggest product to launch"),
        ("Market Demographic Expansion", "Amy Santiago", "Market Expansion", "Expand marketing efforts to target new demographics"),
        ("Turnover Reduction", "Leslie Knope", "Turnover Analysis", "Identify turnover reasons"),
        ("Turnover Reduction", "Ron Swanson", "Anti-turnover Measures", "Implement measures to reduce emplopyee turnover"),
        ("Accelerate Hiring Process", "Leslie Knope", "Hiring Slow-down Reasons", "Identify why hiring is slow"),
        ("Accelerate Hiring Process", "Ron Swanson", "Change Hiring Process", "Modify hiring process to decrease timeline")
    ]
    for product_name, manager_name, name, description in projects:
        add_project(conn, product_name, manager_name, name, description, override=True)
    
    ticket_data = [
        ("Douglas Reynholm", "A.I. Tool Access", "Maurice Moss", "Infrastructure", 
         "Provision LLM API Keys", "Set up enterprise-level access for the engineering team", 5),
        ("Jen Barber", "A.I. Tool Training", "Roy Trenneman", "Analysis", 
         "Inventory AI Competencies", "Survey departments to see who currently uses AI tools", 10),
        ("James Halpert", "Find Process Improvement Areas", "Dwight Schrute", "Analysis", 
         "Analyze Shipping Bottlenecks", "Examine recent downtick in order fulfillment", 3),
        ("Pamela Beesly", "Enforce Process Improvements", "Angela Martin", "New Feature", 
         "Implement Digital Time-Tracking", "Replace paper logs with the new automated system", 14),
        ("Raymond Holt", "Product Suggestion", "Rosa Diaz", "Analysis", 
         "Undercover Market Research", "Analyze competitor pricing", 7),
        ("Terry Jeffords", "Market Expansion", "Jake Peralta", "New Feature", 
         "Target Youth Demographic", "Create a 'cool' ad campaign", 21),
        ("Ron Swanson", "Hiring Slow-down Reasons", "April Ludgate", "Bug Fix", 
         "Fix Job Portal Error", "The 'Apply' button currently deletes the resume. Fix immediately", 2),
        ("Leslie Knope", "Change Hiring Process", "Donna Meagle", "New Feature", 
         "Streamline Background Checks", "Partner with external vendors to reduce check time by 4 days", 30),
        ("Ben Wyatt", "Turnover Analysis", "April Ludgate", "Analysis", 
         "Exit Interview Meta-Analysis", "Identify recurring themes in the last 12 months of exits", 12),
        ("Jack Donaghy", "A.I. Tool Access", "Tracy Jordan", "Infrastructure", 
         "AI Budget Forecasting", "Configure the AI to predict budget overruns", 15)
    ]

    for req, proj, asgn, req_type, t_name, desc, days in ticket_data:
        # Calculate due date based on current date
        due = date.today() + timedelta(days=days)
        
        # Call your add_ticket function
        add_ticket(
            conn=conn,
            requester_name=req,
            project_name=proj,
            assignee_name=asgn,
            request_type_name=req_type,
            name=t_name,
            description=desc,
            due_date=due,
            override=True
        )