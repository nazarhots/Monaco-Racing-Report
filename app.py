import configparser

from flask_restful import Api
from flasgger import Swagger, swag_from
from flask import Flask, render_template, redirect, url_for, request, jsonify, abort
from dict2xml import dict2xml

from race_report import abbr_decoder, drivers_best_lap, build_report


app = Flask(__name__)
api = Api(app)
swagger = Swagger(app, template_file="swag_forms/report.yml")

config = configparser.ConfigParser()
config.read("config.ini")

abbreviations_file = config["Files"]["Abbreviations"]
start_log_file = config["Files"]["StartLog"]
end_log_file = config["Files"]["EndLog"]


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


@app.route("/")
def index():
    return redirect(url_for("report"))


@app.route("/report/")
def report():
    drivers_info = abbr_decoder(abbreviations_file)
    drivers_lap = drivers_best_lap(start_log_file, end_log_file)
    report = build_report(drivers_info, drivers_lap)
    desc_order = request.args.get("order") == "desc"
    if desc_order:
        report = {key: value for key, value in reversed(report.items())}
    return render_template("report.html", drivers_info=report)


@app.route("/report/drivers/")
def report_drivers():
    desc_order = request.args.get("order") == "desc"
    drivers_info = abbr_decoder(abbreviations_file)
    drivers_info = sorted(drivers_info.items(), key=lambda x: x[1]["name"], reverse=desc_order)
    return render_template("report_drivers.html", drivers_info=drivers_info)


@app.route("/report/drivers/<driver_id>")
def report_driver(driver_id):
    drivers_info = abbr_decoder(abbreviations_file)
    driver_info = drivers_info.get(driver_id)
    if not driver_info:
        abort(404)

    driver_name = driver_info.get("name")
    drivers_lap = drivers_best_lap(start_log_file, end_log_file)
    report = build_report(drivers_info, drivers_lap)
    driver = report.get(driver_name)
    return render_template("driver_info.html", driver_info=driver_info, driver=driver)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html"), 404


@app.route("/api/v1/report/", methods=["GET"])
@swag_from("swag_forms/report.yml")
def report_api():
    """Generate a report in JSON or XML format."""
    drivers_info = abbr_decoder(abbreviations_file)
    drivers_lap = drivers_best_lap(start_log_file, end_log_file)
    report = build_report(drivers_info, drivers_lap)
    parser = request.args.get("format")
    
    response = format_response(parser=parser, data=report)
    return response


@app.route("/api/v1/report/drivers/", methods=["GET"])
@swag_from("swag_forms/report.yml")
def report_drivers_api():
    """Retrieve information about drivers in JSON or XML format."""
    drivers_info = abbr_decoder(abbreviations_file)
    parser = request.args.get("format")
    
    responce = format_response(parser=parser, data=drivers_info)
    return responce
    

@app.route("/api/v1/report/drivers/<driver_abbr>", methods=["GET"])
def report_driver_api(driver_abbr):
    """Retrieve information about driver in JSON or XML format."""
    drivers_info = abbr_decoder(abbreviations_file)
    parser = request.args.get("format")
    
    if driver_abbr not in drivers_info:
        abort(404)
    driver_info = drivers_info[driver_abbr]
    
    response = format_response(parser=parser, data=driver_info)
    return response


if __name__ == "__main__":
    app.run()
