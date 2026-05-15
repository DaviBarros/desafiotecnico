from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.security import decode_token
from app.infrastructure.repositories import SqlAlchemyTaskRepository, SqlAlchemyUserRepository


bearer_scheme = HTTPBearer(auto_error=False)


def get_user_repository(session: Session = Depends(get_db_session)) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session)


def get_task_repository(session: Session = Depends(get_db_session)) -> SqlAlchemyTaskRepository:
    return SqlAlchemyTaskRepository(session)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> int:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    try:
        payload = decode_token(credentials.credentials)
        subject = payload.get("sub")
        if subject is None:
            raise ValueError("Missing token subject")
        return int(subject)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
