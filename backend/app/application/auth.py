from app.core.security import create_access_token, hash_password, verify_password
from app.domain.entities import User
from app.domain.exceptions import AuthenticationError, ConflictError
from app.domain.repositories import UserRepository


class RegisterUserUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def execute(self, email: str, password: str) -> User:
        existing_user = self.user_repository.get_by_email(email)
        if existing_user is not None:
            raise ConflictError("Email is already registered")

        hashed_password = hash_password(password)
        return self.user_repository.create(email=email, hashed_password=hashed_password)


class AuthenticateUserUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def execute(self, email: str, password: str) -> str:
        user = self.user_repository.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid credentials")

        return create_access_token(subject=str(user.id))
