import os

from flask_restful import Api
from flasgger import Swagger, swag_from
from flask import Flask, render_template, redirect, url_for, request, jsonify, abort
from dict2xml import dict2xml
from dotenv import load_dotenv
from peewee import PeeweeException, DatabaseError

from race_report import abbr_decoder, drivers_best_lap, build_report
from db_utils import add_drivers_to_db
from models import DriverModel
from logger.logger import create_report_logger


app = Flask(__name__)
api = Api(app)
load_dotenv()
swagger = Swagger(app, template_file=os.getenv("SWAG_REPORT_PATH"))
logger = create_report_logger()


def format_response(parser: str, data: dict):
    """Format the response based on the parser type.

    Args:
        parser (str): The parser type ("json" or "xml").
        data (dict): The data to be formatted.
    """
    if parser.lower() == "json":
        return jsonify(data), 200
    elif parser.lower() == "xml":
        return dict2xml(data), 200
    else:
        logger.error(f"Invalid parser type {parser}")
        abort(400, f"Invalid parser type {parser}. Supported types: JSON, XML")


def get_drivers_query(query, order_by, desc: bool = False):
    """Get a sorted query of drivers. """
    if desc:
        return query.order_by(order_by.desc())
    return query.order_by(order_by)


def initialize_app():
    abbreviations_path = os.getenv("ABBREVIATIONS_PATH")
    startlog_path = os.getenv("STARTLOG_PATH")
    endlog_path = os.getenv("ENDLOG_PATH")
    
    drivers_info = abbr_decoder(abbreviations_path)
    drivers_lap = drivers_best_lap(startlog_path, endlog_path)
    report = build_report(drivers_info, drivers_lap)
    add_drivers_to_db(report)
    

@app.errorhandler(ValueError)
@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html"), 404


@app.errorhandler(PeeweeException)
@app.errorhandler(DatabaseError)
def handle_database_error(error):
    logger.error("An error occurred during database operation")
    abort(500, str(error))


@app.route("/")
def index():
    return redirect(url_for("report"))


@app.route("/report/")
def report():
    desc_order = request.args.get("order") == "desc"
    query = DriverModel.select()
    sorted_query = get_drivers_query(query, DriverModel.place, desc_order)
    return render_template("report.html", drivers_info=sorted_query)


@app.route("/report/drivers/")
def report_drivers():
    desc_order = request.args.get("order") == "desc"
    query = DriverModel.select()
    sorted_query = get_drivers_query(query, DriverModel.name, desc_order)
    return render_template("report_drivers.html", drivers_info=sorted_query)


@app.route("/report/drivers/<driver_id>")
def report_driver(driver_id):
    driver = DriverModel.select().where(DriverModel.abbr == driver_id).first()
    if not driver:
        logger.error(f"Driver '{driver_id}' not found")
        raise ValueError
    return render_template("driver_info.html", driver=driver)


@app.route("/api/v1/report/", methods=["GET"])
@swag_from("swag_forms/report.yml")
def report_api():
    """Generate a report in JSON or XML format. """
    parser = request.args.get("format")
    query = DriverModel.select()
    json_data = [driver.serialize_report() for driver in query]
    response = format_response(parser=parser, data=json_data)
    return response


@app.route("/api/v1/report/drivers/", methods=["GET"])
@swag_from("swag_forms/report.yml")
def report_drivers_api():
    """Retrieve information about drivers in JSON or XML format."""
    parser = request.args.get("format")
    query = DriverModel.select().order_by(DriverModel.name)
    json_data = [driver.serialize_drivers() for driver in query]
    response = format_response(parser=parser, data=json_data)
    return response


@app.route("/api/v1/report/drivers/<driver_abbr>", methods=["GET"])
def report_driver_api(driver_abbr):
    """Retrieve information about driver in JSON or XML format."""
    parser = request.args.get("format")
    driver_info = DriverModel.select().where(DriverModel.abbr == driver_abbr).first()
    if not driver_info:
        logger.error(f"Driver '{driver_abbr}' not found")
        raise ValueError
    json_data = DriverModel.serialize_drivers(driver_info)
    response = format_response(parser=parser, data=json_data)
    return response


if __name__ == "__main__":
    initialize_app()
    app.run()
