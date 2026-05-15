from datetime import datetime
from typing import Dict, List, Optional

from app.application.auth import AuthenticateUserUseCase, RegisterUserUseCase
from app.application.tasks import CreateTaskUseCase, DeleteTaskUseCase, ListTasksUseCase, UpdateTaskUseCase
from app.domain.entities import Task, User
from app.domain.exceptions import AuthenticationError, ConflictError, NotFoundError, PermissionDeniedError


class FakeUserRepository:
    def __init__(self) -> None:
        self.users: Dict[str, User] = {}
        self.sequence = 1

    def create(self, email: str, hashed_password: str) -> User:
        user = User(
            id=self.sequence,
            email=email,
            hashed_password=hashed_password,
            created_at=datetime.utcnow(),
        )
        self.users[email] = user
        self.sequence += 1
        return user

    def get_by_email(self, email: str) -> Optional[User]:
        return self.users.get(email)

    def get_by_id(self, user_id: int) -> Optional[User]:
        for user in self.users.values():
            if user.id == user_id:
                return user
        return None


class FakeTaskRepository:
    def __init__(self, tasks: List[Task]) -> None:
        self.tasks = {task.id: task for task in tasks}
        self.sequence = max(self.tasks.keys(), default=0) + 1

    def create(self, owner_id: int, title: str, description: Optional[str]) -> Task:
        task = Task(
            id=self.sequence,
            title=title,
            description=description,
            is_completed=False,
            owner_id=owner_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.tasks[task.id] = task
        self.sequence += 1
        return task

    def list_by_owner(self, owner_id: int) -> List[Task]:
        return [task for task in self.tasks.values() if task.owner_id == owner_id]

    def get_by_id(self, task_id: int) -> Optional[Task]:
        return self.tasks.get(task_id)

    def update(self, task_id: int, *, title, description, is_completed) -> Task:
        task = self.tasks[task_id]
        updated_task = Task(
            id=task.id,
            title=title if title is not None else task.title,
            description=description if description is not None else task.description,
            is_completed=is_completed if is_completed is not None else task.is_completed,
            owner_id=task.owner_id,
            created_at=task.created_at,
            updated_at=datetime.utcnow(),
        )
        self.tasks[task_id] = updated_task
        return updated_task

    def delete(self, task_id: int) -> None:
        self.tasks.pop(task_id, None)


def test_register_user_rejects_duplicate_email() -> None:
    repository = FakeUserRepository()
    use_case = RegisterUserUseCase(repository)

    use_case.execute("owner@example.com", "secret123")

    try:
        use_case.execute("owner@example.com", "secret123")
        assert False, "expected duplicate email to raise"
    except ConflictError:
        assert True


def test_create_task_returns_task_for_owner() -> None:
    repository = FakeTaskRepository([])
    use_case = CreateTaskUseCase(repository)

    task = use_case.execute(10, "Nova tarefa", "Descricao da tarefa")

    assert task.id == 1
    assert task.title == "Nova tarefa"
    assert task.description == "Descricao da tarefa"
    assert task.is_completed is False
    assert task.owner_id == 10


def test_authenticate_user_rejects_invalid_password() -> None:
    repository = FakeUserRepository()
    RegisterUserUseCase(repository).execute("owner@example.com", "secret123")
    use_case = AuthenticateUserUseCase(repository)

    try:
        use_case.execute("owner@example.com", "wrong-password")
        assert False, "expected invalid credentials to raise"
    except AuthenticationError:
        assert True


def test_list_tasks_returns_only_owner_tasks() -> None:
    task_a = Task(
        id=1,
        title="Task A",
        description=None,
        is_completed=False,
        owner_id=10,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    task_b = Task(
        id=2,
        title="Task B",
        description=None,
        is_completed=False,
        owner_id=20,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    repository = FakeTaskRepository([task_a, task_b])

    tasks = ListTasksUseCase(repository).execute(10)

    assert len(tasks) == 1
    assert tasks[0].id == 1


def test_owner_can_update_task_status() -> None:
    task = Task(
        id=1,
        title="Original",
        description="Descricao",
        is_completed=False,
        owner_id=10,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    repository = FakeTaskRepository([task])

    updated_task = UpdateTaskUseCase(repository).execute(10, 1, title=None, description=None, is_completed=True)

    assert updated_task.id == 1
    assert updated_task.is_completed is True
    assert updated_task.title == "Original"


def test_update_task_raises_when_task_does_not_exist() -> None:
    repository = FakeTaskRepository([])
    use_case = UpdateTaskUseCase(repository)

    try:
        use_case.execute(10, 999, title="Changed", description=None, is_completed=True)
        assert False, "expected missing task to raise"
    except NotFoundError:
        assert True


def test_only_owner_can_update_task() -> None:
    task = Task(
        id=1,
        title="Original",
        description=None,
        is_completed=False,
        owner_id=10,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    repository = FakeTaskRepository([task])
    use_case = UpdateTaskUseCase(repository)

    try:
        use_case.execute(20, 1, title="Changed", description=None, is_completed=True)
        assert False, "expected permission error"
    except PermissionDeniedError:
        assert True


def test_only_owner_can_delete_task() -> None:
    task = Task(
        id=1,
        title="Original",
        description=None,
        is_completed=False,
        owner_id=10,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    repository = FakeTaskRepository([task])
    use_case = DeleteTaskUseCase(repository)

    try:
        use_case.execute(20, 1)
        assert False, "expected permission error"
    except PermissionDeniedError:
        assert True


def test_delete_task_raises_when_task_does_not_exist() -> None:
    repository = FakeTaskRepository([])
    use_case = DeleteTaskUseCase(repository)

    try:
        use_case.execute(10, 999)
        assert False, "expected missing task to raise"
    except NotFoundError:
        assert True
