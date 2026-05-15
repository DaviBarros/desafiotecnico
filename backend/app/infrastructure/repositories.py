from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import Task, User
from app.infrastructure.models import TaskModel, UserModel


def _to_user_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        hashed_password=model.hashed_password,
        created_at=model.created_at,
    )


def _to_task_entity(model: TaskModel) -> Task:
    return Task(
        id=model.id,
        title=model.title,
        description=model.description,
        is_completed=model.is_completed,
        owner_id=model.owner_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyUserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, email: str, hashed_password: str) -> User:
        user = UserModel(email=email, hashed_password=hashed_password)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return _to_user_entity(user)

    def get_by_email(self, email: str) -> Optional[User]:
        statement = select(UserModel).where(UserModel.email == email)
        user = self.session.execute(statement).scalar_one_or_none()
        return _to_user_entity(user) if user else None

    def get_by_id(self, user_id: int) -> Optional[User]:
        statement = select(UserModel).where(UserModel.id == user_id)
        user = self.session.execute(statement).scalar_one_or_none()
        return _to_user_entity(user) if user else None


class SqlAlchemyTaskRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, owner_id: int, title: str, description: Optional[str]) -> Task:
        task = TaskModel(owner_id=owner_id, title=title, description=description)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return _to_task_entity(task)

    def list_by_owner(self, owner_id: int) -> List[Task]:
        statement = select(TaskModel).where(TaskModel.owner_id == owner_id).order_by(TaskModel.created_at.desc())
        tasks = self.session.execute(statement).scalars().all()
        return [_to_task_entity(task) for task in tasks]

    def get_by_id(self, task_id: int) -> Optional[Task]:
        statement = select(TaskModel).where(TaskModel.id == task_id)
        task = self.session.execute(statement).scalar_one_or_none()
        return _to_task_entity(task) if task else None

    def update(
        self,
        task_id: int,
        *,
        title: Optional[str],
        description: Optional[str],
        is_completed: Optional[bool]
    ) -> Task:
        task = self.session.get(TaskModel, task_id)
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if is_completed is not None:
            task.is_completed = is_completed
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return _to_task_entity(task)

    def delete(self, task_id: int) -> None:
        task = self.session.get(TaskModel, task_id)
        self.session.delete(task)
        self.session.commit()
