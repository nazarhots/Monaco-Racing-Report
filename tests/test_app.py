import xml.etree.ElementTree as ET
from unittest.mock import patch

from flask import url_for
from bs4 import BeautifulSoup
from peewee import PeeweeException, DatabaseError

from app import app
from models import DriverModel


app.config["SERVER_NAME"] = "localhost"


def count_class_elements(html: str, element: str) -> int:
    """Count the number of elements with a specific class in an HTML string."""
    soup = BeautifulSoup(html, "html.parser")
    elements = soup.find_all(class_=element)
    elements_amount = len(elements)
    return elements_amount


def assert_driver_order(response, first_driver, second_driver):
    """Asserts the order of drivers in the response."""
    soup = BeautifulSoup(response.text, "html.parser")
    driver_name_elements = soup.find_all(class_="driver-name")
    last_place_index = driver_name_elements.index(soup.find("span", class_="driver-name", string=first_driver))
    first_place_index = driver_name_elements.index(soup.find("span", class_="driver-name", string=second_driver))

    assert last_place_index > first_place_index


def test_index_redirect(client):
    response = client.get("/")
    
    assert response.status_code == 302
    assert "report" in response.location


def test_report_order_asc(client):
    response = client.get(url_for("report"))
    
    driver_first_place = DriverModel.select().where(DriverModel.place == 1).first()
    driver_second_place = DriverModel.select().where(DriverModel.place == 2).first()
    response_text_with_first_place = response.text.split("<td>2.</td>")[0]

    assert_driver_order(response, driver_second_place.name, driver_first_place.name)
    assert response.status_code == 200
    assert driver_first_place.name in response_text_with_first_place
    assert driver_second_place.name not in response_text_with_first_place


def test_report_order_desc(client):
    response = client.get(url_for("report", order="desc"))
    
    drivers_number = count_class_elements(response.text, "driver-name")
    driver_last_place = DriverModel.select().where(DriverModel.place == drivers_number).first()
    driver_first_place = DriverModel.select().where(DriverModel.place == 1).first()
    response_text_with_last_place = response.text.split("<td>2.</td>")[0]

    assert_driver_order(response, driver_first_place.name, driver_last_place.name)
    assert response.status_code == 200
    assert driver_last_place.name in response_text_with_last_place
    assert driver_first_place.name not in response_text_with_last_place


def test_report_exception(client):
    with patch("app.DriverModel.select") as mock:
        mock.side_effect = PeeweeException()
        response = client.get(url_for("report"))
        
        assert response.status_code == 500


def test_report_drivers(client):
    response = client.get(url_for("report_drivers"))

    assert response.status_code == 200
    assert b"Driver Name" in response.data
    assert b"Abbreviations" in response.data


def test_report_drivers_order_asc(client):
    response = client.get(url_for("report_drivers"))
    driver_name = DriverModel.select().where(DriverModel.place == 1).first().name
    driver_abbr = DriverModel.select().where(DriverModel.place == 1).first().abbr
    
    assert response.status_code == 200
    assert driver_name in response.text
    assert driver_abbr in response.text


def test_report_drivers_order_desc(client):
    response = client.get(url_for("report_drivers", order="desc"))
    driver_name = DriverModel.select().where(DriverModel.place == 1).first().name
    driver_abbr = DriverModel.select().where(DriverModel.place == 1).first().abbr
    
    assert response.status_code == 200
    assert driver_name in response.text
    assert driver_abbr in response.text


def test_report_drivers_exception(client):
    with patch("app.DriverModel.select") as mock:
        mock.side_effect = PeeweeException()
        response = client.get(url_for("report_drivers"))
        
        assert response.status_code == 500


def test_report_driver_info(client):
    driver = DriverModel.select().where(DriverModel.place == 1).first()
    response = client.get(url_for("report_driver", driver_id=driver.abbr))
    
    assert response.status_code == 200
    assert driver.name in response.text
    

def test_report_driver_info_invalid_data(client):
    response = client.get(url_for("report_driver", driver_id="TEST"))

    assert response.status_code == 404


def test_report_driver_exception(client):
    with patch("app.DriverModel.select") as mock:
        mock.side_effect = PeeweeException()
        response = client.get(url_for("report_driver", driver_id="SVF"))
        
        assert response.status_code == 500


def test_page_not_found(client):
    response = client.get("/my_test_url")

    assert response.status_code == 404


def test_report_api_json(client):
    response = client.get(url_for("report_api", format="json"))
    
    driver = DriverModel.select().where(DriverModel.place == 1).first()
    expected_data = {"abbr": driver.abbr, 
                     "best_lap": driver.best_lap, 
                     "name": driver.name, 
                     "place": driver.place, 
                     "team": driver.team}

    assert expected_data == response.get_json()[0]
    assert response.status_code == 200


def test_report_api_xml(client):
    response = client.get(url_for("report_api", format="xml"))
    
    driver = DriverModel.select().where(DriverModel.place == 1).first()    
    text = response.text.strip()
    driver_xml = f"<root>{text}</root>"
    root = ET.fromstring(driver_xml)
    
    response_name = root.find("name").text
    response_abbr = root.find("abbr").text
    response_team = root.find("team").text
    response_place = int(root.find("place").text)
    response_best_lap = root.find("best_lap").text
    
    assert driver.name == response_name
    assert driver.abbr == response_abbr
    assert driver.team == response_team
    assert driver.place == response_place
    assert driver.best_lap == response_best_lap
    assert response.status_code == 200
    

def test_report_api_exception(client):
    with patch("app.DriverModel.select") as mock:
        mock.side_effect = PeeweeException()
        response = client.get(url_for("report_api"))
        
        assert response.status_code == 500


def test_report_drivers_api_json(client):
    response = client.get(url_for("report_drivers_api", format="json"))
    
    driver = DriverModel.select().order_by(DriverModel.name).first()
    driver_json_response = response.get_json()[0]
    colomns_number = len(driver_json_response)
    
    assert response.status_code == 200
    assert colomns_number == 2
    assert driver.name == driver_json_response["name"]
    assert driver.team == driver_json_response["team"]
    

def test_report_drivers_api_xml(client):
    response = client.get(url_for("report_drivers_api", format="xml"))
    
    driver = DriverModel.select().order_by(DriverModel.name).first()
    text = response.text.strip()
    driver_xml = f"<root>{text}</root>"
    root = ET.fromstring(driver_xml)
    
    responce_name = root.find("name").text
    response_team = root.find("team").text

    assert driver.name == responce_name
    assert driver.team == response_team


def test_report_drivers_api_exception(client):
    with patch("app.DriverModel.select") as mock:
        mock.side_effect = PeeweeException()
        response = client.get(url_for("report_drivers_api"))
        
        assert response.status_code == 500


def test_report_driver_api_valid_json(client):
    driver = DriverModel.select().first()
    response = client.get(url_for("report_driver_api", driver_abbr=driver.abbr, format="json"))
    driver_json_response = response.get_json()
    
    assert driver.name == driver_json_response["name"]
    assert driver.team == driver_json_response["team"]
    assert response.status_code == 200


def test_report_driver_api_valid_xml(client):
    driver = DriverModel.select().first()
    response = client.get(url_for("report_driver_api", driver_abbr=driver.abbr, format="xml"))
    
    text = response.text.strip()
    driver_xml = f"<root>{text}</root>"
    root = ET.fromstring(driver_xml)
    
    responce_name = root.find("name").text
    response_team = root.find("team").text
    
    assert driver.name == responce_name
    assert driver.team == response_team
    assert response.status_code == 200
    
    
def test_report_driver_invalid_data(client):
    response = client.get("/api/v1/report/drivers/TEST?format=xml")
    
    assert response.status_code == 404


def test_report_driver_api_exception(client):
    with patch("app.DriverModel.select") as mock:
        mock.side_effect = PeeweeException()
        response = client.get(url_for("report_driver_api", driver_abbr="SVF"))
        
        assert response.status_code == 500
