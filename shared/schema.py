import sqlite3
from shared import entities
import inspect
from dataclasses import fields, is_dataclass
from datetime import date

def database_conn() -> sqlite3.Connection:
    return sqlite3.connect("c3po.db")

def create_table(conn: sqlite3.Connection, table_name: str) -> None:
    query = f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT);"
    conn.execute(query)
    conn.commit()

def grab_existing_columns(conn: sqlite3.Connection, table_name) -> list:
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]

def add_column(conn: sqlite3.Connection, table_name: str, col_name: str, col_type: str) -> None:
    existing_columns = grab_existing_columns(conn, table_name)
    if col_name not in existing_columns:
        query = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"
        conn.execute(query)
        conn.commit()

def get_db_type(py_type) -> str:
    origin = getattr(py_type, "__origin__", None)
    if origin is not None:
        py_type = py_type.__args__[0]
    
    mapping = {
        int: "INTEGER",
        str: "TEXT",
        float: "REAL",
        bool: "INTEGER",
        date: "DATE"
    }
    return mapping.get(py_type, "TEXT")

def grab_dataclasses() -> list:
    return [
        value for name, value in inspect.getmembers(entities)
        if inspect.isclass(value) and is_dataclass(value)
    ]

def camel_to_snake(dataclass) -> str:
    return "".join(["_" + c.lower() if c.isupper() else c for c in dataclass.__name__]).lstrip("_")

def create_db_pipeline() -> sqlite3.Connection:
    conn = database_conn()

    entities = grab_dataclasses()

    for table in entities:
        table_name = camel_to_snake(table)
        create_table(conn, table_name)
        for column in fields(table):
            if column.name == 'id':
                continue
            db_type = get_db_type(column.type)
            add_column(conn, table_name, column.name, db_type)

    return conn