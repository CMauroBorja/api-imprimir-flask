import logging


class AppException(Exception):
    """Excepción base de la aplicación."""

    status_code = 500
    log_level = logging.ERROR

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class ValidationError(AppException):
    status_code = 400
    log_level = logging.WARNING


class UnauthorizedError(AppException):
    status_code = 401
    log_level = logging.WARNING


class ForbiddenError(AppException):
    status_code = 403
    log_level = logging.WARNING


class NotFoundError(AppException):
    status_code = 404
    log_level = logging.INFO


class ConflictError(AppException):
    status_code = 409
    log_level = logging.WARNING


class DatabaseError(AppException):
    status_code = 500
    log_level = logging.ERROR
    

class PrinterError(AppException):
    status_code = 500
    log_level = logging.ERROR