from dataclasses import *
from datetime import date
from typing import Optional

# User
@dataclass(frozen=True)
class User:
    id: Optional[int]
    management_level_id: int
    team_id: int
    name: str
    username: str
    active_status: bool

# Management Level
@dataclass(frozen=True)
class ManagementLevel:
    id: Optional[int]
    name: str
    seniority_score: int

# Team
@dataclass(frozen=True)
class Team:
    id: Optional[int]
    name: str
    description: str

# Ticket
@dataclass(frozen=True)
class Ticket:
    id: Optional[int]
    requester_id: int
    project_id: Optional[int]
    assignee_id: Optional[int]
    request_type_id: int
    name: str
    description: str
    due_date: Optional[date]
    start_date: Optional[date]
    end_date: Optional[date]
    estimated_duration_time: Optional[int]
    estimated_duration_units: Optional[int]
    status_id: int

# Project
@dataclass(frozen=True)
class Project:
    id: Optional[int]
    product_id: Optional[int]
    manager_id: Optional[int]
    name: str
    description: str

# Product
@dataclass(frozen=True)
class Product:
    id: Optional[int]
    portfolio_id: Optional[int]
    manager_id: Optional[int]
    name: str
    description: str

# Portfolio
@dataclass(frozen=True)
class Portfolio:
    id: Optional[int]
    name: str
    description: str

# Status
@dataclass(frozen=True)
class Status:
    id: Optional[int]
    name: str

# Request Type
@dataclass(frozen=True)
class RequestType:
    id: Optional[int]
    name: str

# Estimated Duration Units
@dataclass(frozen=True)
class DurationUnits:
    id: Optional[int]
    name: str