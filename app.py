from flask_restful import Api
from flasgger import Swagger, swag_from
from flask import Flask, render_template, redirect, url_for, request, jsonify, abort
from dict2xml import dict2xml

from race_report import abbr_decoder, drivers_best_lap, build_report
from db_utils import add_drivers_to_db
from models import DriverModel
from config import abbreviations_file, start_log_file, end_log_file


app = Flask(__name__)
api = Api(app)
swagger = Swagger(app, template_file="swag_forms/report.yml")


def format_response(parser: str, data: dict):
    """Format the response based on the parser type.

    Args:
        parser (str): The parser type ("json" or "xml").
        data (dict): The data to be formatted.
    """
    if parser == "json":
        return jsonify(data), 200
    elif parser == "xml":
        return dict2xml(data), 200
    else:
        abort(404)


def get_drivers_query(query, order_by, desc: bool = False):
    """Get a sorted query of drivers. """
    if desc:
        return query.order_by(order_by.desc())
    return query.order_by(order_by)


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
        abort(404)
    return render_template("driver_info.html", driver=driver)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html"), 404


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
        abort(404)
    json_data = DriverModel.serialize_drivers(driver_info)
    response = format_response(parser=parser, data=json_data)
    return response


if __name__ == "__main__":
    drivers_info = abbr_decoder(abbreviations_file)
    drivers_lap = drivers_best_lap(start_log_file, end_log_file)
    report = build_report(drivers_info, drivers_lap)
    add_drivers_to_db(report)
    app.run()
