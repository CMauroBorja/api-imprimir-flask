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

    response, status = login_user(
        request.json
    )

    return jsonify(
        response
    ), status