from flask import jsonify

from app.exceptions.custom_exceptions import AppException
from app.config.logging_config import logger


def register_error_handlers(app):

    @app.errorhandler(AppException)
    def handle_app_exception(error):

        logger.log(error.log_level, error.message)

        return jsonify({
            "error": error.message
        }), error.status_code


    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):

        logger.exception(error)

        return jsonify({
            "error": "Ha ocurrido un error interno."
        }), 500