from typing import List, Optional, Protocol

from app.domain.entities import Task, User


class UserRepository(Protocol):
    def create(self, email: str, hashed_password: str) -> User:
        ...

    def get_by_email(self, email: str) -> Optional[User]:
        ...

    def get_by_id(self, user_id: int) -> Optional[User]:
        ...


class TaskRepository(Protocol):
    def create(self, owner_id: int, title: str, description: Optional[str]) -> Task:
        ...

    def list_by_owner(self, owner_id: int) -> List[Task]:
        ...

    def get_by_id(self, task_id: int) -> Optional[Task]:
        ...

    def update(
        self,
        task_id: int,
        *,
        title: Optional[str],
        description: Optional[str],
        is_completed: Optional[bool]
    ) -> Task:
        ...

    def delete(self, task_id: int) -> None:
        ...
