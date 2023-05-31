from unittest.mock import patch
import xml.etree.ElementTree as ET
import json

import pytest
from flask import url_for
from bs4 import BeautifulSoup

from app import app
from .param_data import param_for_abbr_decoder, param_for_drivers_best_lap


app.config["SERVER_NAME"] = "localhost"


def count_class_elements(html: str, element: str) -> int:
    """Count the number of elements with a specific class in an HTML string."""
    soup = BeautifulSoup(html, "html.parser")
    elements = soup.find_all(class_=element)
    elements_amount = len(elements)
    return elements_amount


def assert_driver_order(response, last_driver, first_driver):
    """Asserts the order of drivers in the response."""
    soup = BeautifulSoup(response.text, "html.parser")
    driver_name_elements = soup.find_all(class_="driver-name")
    last_place_index = driver_name_elements.index(soup.find("span", class_="driver-name", string=last_driver))
    first_place_index = driver_name_elements.index(soup.find("span", class_="driver-name", string=first_driver))

    assert last_place_index > first_place_index


def test_index_redirect(client):
    response = client.get("/")
    
    assert response.status_code == 302
    assert "report" in response.location


@pytest.mark.parametrize("data", [b"Place", b"Driver", b"Team", b"Best Lap"])
def test_report_order(client, data):
    response = client.get(url_for("report"))
    
    assert data in response.data


@patch("app.abbr_decoder", return_value=param_for_abbr_decoder)
@patch("app.drivers_best_lap", return_value=param_for_drivers_best_lap)
def test_report_order_asc(abbr_mock, drivers_mock, client):
    response = client.get(url_for("report"))
    response_text_with_first_place = response.text.split("<td>2.</td>")[0]
    elements_number = count_class_elements(response.text, "driver-name")

    assert "Sebastian Vettel" in response_text_with_first_place
    assert "Kimi Raikkonen" not in response_text_with_first_place
    assert "Valtteri Bottas" not in response_text_with_first_place
    assert elements_number == 3


@patch("app.abbr_decoder", return_value=param_for_abbr_decoder)
@patch("app.drivers_best_lap", return_value=param_for_drivers_best_lap)
def test_report_order_desc(abbr_mock, drivers_mock, client):
    response = client.get(url_for("report", order="desc"))
    response_text_with_last_place = response.text.split("<td>2.</td>")[0]
    elements_number = count_class_elements(response.text, "driver-name")

    assert "Valtteri Bottas" in response_text_with_last_place
    assert "Sebastian Vettel" not in response_text_with_last_place
    assert "Kimi Raikkonen" not in response_text_with_last_place
    assert elements_number == 3


def test_report_drivers(client):
    response = client.get(url_for("report_drivers"))

    assert response.status_code == 200
    assert b"Driver Name" in response.data
    assert b"Abbreviations" in response.data


@patch("app.abbr_decoder", return_value=param_for_abbr_decoder)
@patch("app.drivers_best_lap", return_value=param_for_drivers_best_lap)
def test_report_drivers_order_asc(abbr_mock, drivers_mock, client):
    response = client.get(url_for("report_drivers"))
    elements_number = count_class_elements(response.text, "driver-name")

    assert_driver_order(response, "Valtteri Bottas", "Sebastian Vettel")
    
    assert elements_number == 3


@patch("app.abbr_decoder", return_value=param_for_abbr_decoder)
@patch("app.drivers_best_lap", return_value=param_for_drivers_best_lap)
def test_report_drivers_order_desc(abbr_mock, drivers_mock, client):
    response = client.get(url_for("report_drivers", order="desc"))
    elements_number = count_class_elements(response.text, "driver-name")

    assert_driver_order(response, "Sebastian Vettel", "Valtteri Bottas")
    
    assert elements_number == 3


def test_report_driver_info(client):
    response = client.get(url_for("report_driver", driver_id="SVF"))
    elements_number = count_class_elements(response.text, "driver-name")

    assert response.status_code == 200
    assert elements_number == 1
    

def test_report_driver_info_invalid_data(client):
    response = client.get(url_for("report_driver", driver_id="TEST"))

    assert response.status_code == 404
    

def test_page_not_found(client):
    response = client.get("/my_test_url")

    assert response.status_code == 404


@patch("app.abbr_decoder", return_value=param_for_abbr_decoder)
@patch("app.drivers_best_lap", return_value=param_for_drivers_best_lap)
def test_report_api_json(abbr_mock, drivers_mock, client):
    response = client.get("/api/v1/report/?format=json")
   
    data = json.loads(response.text)
    elements_number = len(data)
    expected_data = {
        'Kimi Raikkonen': {'best_lap': '0:01:12.434', 'place': 2, 'team': 'FERRARI'},
        'Sebastian Vettel': {'best_lap': '0:01:04.415', 'place': 1, 'team': 'FERRARI'},
        'Valtteri Bottas': {'best_lap': '0:01:12.618', 'place': 3, 'team': 'MERCEDES'}
    }

    assert elements_number == 3
    assert data == expected_data
    

@patch("app.abbr_decoder", return_value=param_for_abbr_decoder)
@patch("app.drivers_best_lap", return_value=param_for_drivers_best_lap)
def test_report_api_xml(abbr_mock, drivers_mock, client):
    response = client.get("/api/v1/report/?format=xml")
    
    data = response.text
    xml_data = f"<root>{data}</root>"
    root = ET.fromstring(xml_data)
    xml_formatted = ET.tostring(root, encoding='utf-8').decode('utf-8')
    
    expected_data = "root><Kimi_Raikkonen>\n  <best_lap>0:01:12.434</best_lap>\n  <place>2</place>\n  <team>FERRARI"
    
    assert expected_data in xml_formatted
    

@patch("app.abbr_decoder", return_value=param_for_abbr_decoder)
def test_report_drivers_api_json(abbr_mock, client):
    response = client.get("/api/v1/report/drivers/?format=json")
    
    data = json.loads(response.text)
    elements_number = len(data)
    
    expected_data = {
        'KRF': {'name': 'Kimi Raikkonen', 'team': 'FERRARI'},
        'SVF': {'name': 'Sebastian Vettel', 'team': 'FERRARI'},
        'VBM': {'name': 'Valtteri Bottas', 'team': 'MERCEDES'}
    }
    
    assert data == expected_data
    assert elements_number == 3
    

@patch("app.abbr_decoder", return_value=param_for_abbr_decoder)
def test_report_drivers_api_xml(abbr_mock, client):
    response = client.get("/api/v1/report/drivers/?format=xml")
    data = response.text
    
    xml_data = f"<root>{data}</root>"
    root = ET.fromstring(xml_data)
    xml_formatted = ET.tostring(root, encoding='utf-8').decode('utf-8')
    expected_data = "<root><KRF>\n  <name>Kimi Raikkonen</name>\n  <team>FERRARI</team>\n</KRF>\n<SVF>\n"
    
    assert expected_data in xml_formatted
    

@patch("app.abbr_decoder", return_value=param_for_abbr_decoder)
def test_report_driver_api_valid_json(abbr_mock, client):
    response = client.get("/api/v1/report/drivers/SVF?format=json")
    data = json.loads(response.text)
    
    expected_data = {'name': 'Sebastian Vettel', 'team': 'FERRARI'}
    assert data == expected_data
    

@patch("app.abbr_decoder", return_value=param_for_abbr_decoder)
def test_report_driver_api_valid_xml(abbr_mock, client):
    response = client.get("/api/v1/report/drivers/SVF?format=xml")
    
    data = response.text
    xml_data = f"<root>{data}</root>"
    root = ET.fromstring(xml_data)
    xml_formatted = ET.tostring(root, encoding='utf-8').decode('utf-8')
    
    expected_data = "<root><name>Sebastian Vettel</name>\n<team>FERRARI</team></root>"
    
    assert xml_formatted == expected_data
    
    
def test_report_driver_invalid_data(client):
    response = client.get("/api/v1/report/drivers/TEST?format=xml")
    
    assert response.status_code == 404