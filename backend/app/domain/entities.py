from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class User:
    id: int
    email: str
    hashed_password: str
    created_at: datetime


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    description: Optional[str]
    is_completed: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime
