from flask import Blueprint, jsonify, request

from app.services.employee_service import (
    get_all_employees,
    create_employee,
    get_employee_by_id,
    update_employee
)

employee_bp = Blueprint("employees", __name__)


@employee_bp.route("/getAllEmployees", methods=["GET"])
def get_all():

    response, status = get_all_employees()

    return jsonify(response), status


@employee_bp.route("/createEmployee", methods=["POST"])
def create():

    response, status = create_employee(
        request.json
    )

    return jsonify(response), status


@employee_bp.route("/getEmployee/<int:employee_id>", methods=["GET"])
def get_employee(employee_id):

    response, status = get_employee_by_id(
        employee_id
    )

    return jsonify(response), status


@employee_bp.route("/updateEmployee/<codigo>", methods=["PUT"])
def update(codigo):

    response, status = update_employee(
        codigo,
        request.json
    )

    return jsonify(response), status