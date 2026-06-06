from flask import (
    Blueprint,
    jsonify,
    request
)

from app.services.auth_service import (
    login_user
)

auth_bp = Blueprint(
    "auth",
    __name__
)


@auth_bp.route(
    "/login",
    methods=["POST"]
)
def login():

    try:

        response, status = login_user(
            request.json
        )

        return jsonify(
            response
        ), status

    except Exception as e:

        return jsonify({
            "error":
            f"Error al iniciar sesión: {str(e)}"
        }), 500