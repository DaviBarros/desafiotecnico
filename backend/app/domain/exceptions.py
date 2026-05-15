class DomainError(Exception):
    pass


class AuthenticationError(DomainError):
    pass


class ConflictError(DomainError):
    pass


class NotFoundError(DomainError):
    pass


class PermissionDeniedError(DomainError):
    pass
