from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.application.auth import AuthenticateUserUseCase, RegisterUserUseCase
from app.application.tasks import (
    CreateTaskUseCase,
    DeleteTaskUseCase,
    ListTasksUseCase,
    UpdateTaskUseCase,
)
from app.domain.entities import Task, User
from app.domain.exceptions import AuthenticationError, ConflictError, NotFoundError, PermissionDeniedError
from app.infrastructure.repositories import SqlAlchemyTaskRepository, SqlAlchemyUserRepository
from app.presentation.dependencies import get_current_user_id, get_task_repository, get_user_repository
from app.presentation.schemas import (
    LoginRequest,
    TaskCreateRequest,
    TaskResponse,
    TaskUpdateRequest,
    TokenResponse,
    UserCreateRequest,
    UserResponse,
)


api_router = APIRouter(prefix="/api")


def _to_user_response(user: User) -> UserResponse:
    return UserResponse(id=user.id, email=user.email, created_at=user.created_at)


def _to_task_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        is_completed=task.is_completed,
        owner_id=task.owner_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@api_router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserCreateRequest,
    user_repository: SqlAlchemyUserRepository = Depends(get_user_repository),
) -> UserResponse:
    try:
        user = RegisterUserUseCase(user_repository).execute(payload.email, payload.password)
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return _to_user_response(user)


@api_router.post("/auth/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    user_repository: SqlAlchemyUserRepository = Depends(get_user_repository),
) -> TokenResponse:
    try:
        token = AuthenticateUserUseCase(user_repository).execute(payload.email, payload.password)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    return TokenResponse(access_token=token)


@api_router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreateRequest,
    current_user_id: int = Depends(get_current_user_id),
    task_repository: SqlAlchemyTaskRepository = Depends(get_task_repository),
) -> TaskResponse:
    task = CreateTaskUseCase(task_repository).execute(current_user_id, payload.title, payload.description)
    return _to_task_response(task)


@api_router.get("/tasks", response_model=List[TaskResponse])
def list_tasks(
    current_user_id: int = Depends(get_current_user_id),
    task_repository: SqlAlchemyTaskRepository = Depends(get_task_repository),
) -> List[TaskResponse]:
    tasks = ListTasksUseCase(task_repository).execute(current_user_id)
    return [_to_task_response(task) for task in tasks]


@api_router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdateRequest,
    current_user_id: int = Depends(get_current_user_id),
    task_repository: SqlAlchemyTaskRepository = Depends(get_task_repository),
) -> TaskResponse:
    try:
        task = UpdateTaskUseCase(task_repository).execute(
            current_user_id,
            task_id,
            title=payload.title,
            description=payload.description,
            is_completed=payload.is_completed,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return _to_task_response(task)


@api_router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user_id: int = Depends(get_current_user_id),
    task_repository: SqlAlchemyTaskRepository = Depends(get_task_repository),
) -> Response:
    try:
        DeleteTaskUseCase(task_repository).execute(current_user_id, task_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)