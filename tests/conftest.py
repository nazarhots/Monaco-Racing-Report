import os
import shutil
import pytest

from app import app


@pytest.fixture
def create_temp_test_folder():
    current_directory = os.getcwd()
    test_folder = "test data"
    os.makedirs(test_folder)

    abbreviations_path = os.path.join(current_directory, test_folder, "abbreviations.txt")
    start_path = os.path.join(current_directory, test_folder, "start.log")
    end_path = os.path.join(current_directory, test_folder, "end.log")

    with open(abbreviations_path, "w") as abbr:
        data = """DRR_Daniel Ricciardo_RED BULL RACING TAG HEUER
SVF_Sebastian Vettel_FERRARI
LHM_Lewis Hamilton_MERCEDES"""
        abbr.write(data)

    with open(start_path, "w") as start:
        data = """DRR2018-05-24_12:14:12.054
SVF2018-05-24_12:02:58.917
LHM2018-05-24_12:18:20.125"""
        start.write(data)

    with open(end_path, "w") as end:
        data = """DRR2018-05-24_12:15:24.067
SVF2018-05-24_12:04:18.917
LHM2018-05-24_12:19:38.125"""
        end.write(data)

    yield

    if os.path.exists(test_folder):
        shutil.rmtree(test_folder)


@pytest.fixture
def create_path_to_folder():
    current_directory = os.getcwd()
    path_to_folder = os.path.join(current_directory, "test data")
    return path_to_folder


@pytest.fixture
def client():
    with app.app_context():
        with app.test_client() as client:
            yield client
