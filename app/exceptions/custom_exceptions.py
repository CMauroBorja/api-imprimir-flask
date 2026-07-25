class AppException(Exception):
    """Excepción base de la aplicación."""

    status_code = 500

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class ValidationError(AppException):
    status_code = 400


class UnauthorizedError(AppException):
    status_code = 401


class ForbiddenError(AppException):
    status_code = 403


class NotFoundError(AppException):
    status_code = 404


class ConflictError(AppException):
    status_code = 409


class DatabaseError(AppException):
    status_code = 500