from typing import List, Optional

from app.domain.entities import Task
from app.domain.exceptions import NotFoundError, PermissionDeniedError
from app.domain.repositories import TaskRepository


class CreateTaskUseCase:
    def __init__(self, task_repository: TaskRepository) -> None:
        self.task_repository = task_repository

    def execute(self, owner_id: int, title: str, description: Optional[str]) -> Task:
        return self.task_repository.create(owner_id=owner_id, title=title, description=description)


class ListTasksUseCase:
    def __init__(self, task_repository: TaskRepository) -> None:
        self.task_repository = task_repository

    def execute(self, owner_id: int) -> List[Task]:
        return self.task_repository.list_by_owner(owner_id=owner_id)


class UpdateTaskUseCase:
    def __init__(self, task_repository: TaskRepository) -> None:
        self.task_repository = task_repository

    def execute(
        self,
        current_user_id: int,
        task_id: int,
        *,
        title: Optional[str],
        description: Optional[str],
        is_completed: Optional[bool]
    ) -> Task:
        task = self.task_repository.get_by_id(task_id)
        if task is None:
            raise NotFoundError("Task not found")
        if task.owner_id != current_user_id:
            raise PermissionDeniedError("Only the owner can update the task")

        return self.task_repository.update(
            task_id,
            title=title,
            description=description,
            is_completed=is_completed,
        )


class DeleteTaskUseCase:
    def __init__(self, task_repository: TaskRepository) -> None:
        self.task_repository = task_repository

    def execute(self, current_user_id: int, task_id: int) -> None:
        task = self.task_repository.get_by_id(task_id)
        if task is None:
            raise NotFoundError("Task not found")
        if task.owner_id != current_user_id:
            raise PermissionDeniedError("Only the owner can delete the task")

        self.task_repository.delete(task_id)
