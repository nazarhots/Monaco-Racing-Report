from unittest.mock import patch, mock_open

import pytest

from race_report import abbr_decoder, drivers_best_lap, build_report, read_race_data
from .param_data import param_for_abbr_decoder, param_for_drivers_best_lap


def assert_raises_exception(expected_exception, func, *args, **kwargs):
    with pytest.raises(expected_exception):
        func(*args, **kwargs)


def test_abbr_decoder_file_path_valid_data():
    data = "DRR_Daniel Ricciardo_RED BULL RACING TAG HEUER"
    expected_data = {"DRR": {"name": "Daniel Ricciardo",
                             "team": "RED BULL RACING TAG HEUER"}}
    mock_file = mock_open(read_data=data)
    with patch("builtins.open", mock_file):
        result = abbr_decoder("path_to_file")
        assert result == expected_data


def test_abbr_decoder_file_not_found():
    assert_raises_exception(FileNotFoundError, abbr_decoder, "path_to_file")


def test_abbr_decoder_access_failed():
    test_cases = [PermissionError, IsADirectoryError,
                  UnicodeDecodeError("", b"", 0, 1, ""), IOError]
    for exception in test_cases:
        with patch("builtins.open", side_effect=exception):
            assert_raises_exception(OSError, abbr_decoder, "path_to_file")


def test_abbr_decoder_unexpected_error():
    assert_raises_exception(Exception, abbr_decoder, "path_to_file")


def test_read_race_data_lap_valid_data():
    data = "SVF2018-05-24_12:02:58.917\nNHR2018-05-24_12:02:49.914"
    expected_data = {"SVF": "2018-05-24_12:02:58.917",
                     "NHR": "2018-05-24_12:02:49.914"}
    mock_file = mock_open(read_data=data)
    with patch("builtins.open", mock_file):
        result = read_race_data("path_to_file")
        assert result == expected_data


def test_read_race_data_file_not_found():
    assert_raises_exception(FileNotFoundError, read_race_data, "path_to_file")


def test_read_race_data_failed():
    test_cases = [PermissionError, IsADirectoryError,
                  UnicodeDecodeError("", b"", 0, 1, ""), IOError]
    for exception in test_cases:
        with patch("builtins.open", side_effect=exception):
            assert_raises_exception(OSError, read_race_data, "path_to_file")


def test_read_race_data_unexpected_error():
    assert_raises_exception(Exception, read_race_data, "path_to_start_file")


def test_drivers_best_lap_valid_data():
    time_start = "SVF2018-05-24_12:02:58.917\nNHR2018-05-24_12:02:49.914"
    time_finish = "SVF2018-05-24_12:04:03.332\nNHR2018-05-24_12:04:02.979"
    expected_data = {"SVF": "0:01:04.415", "NHR": "0:01:13.065"}
    mock_file_start = mock_open(read_data=time_start)
    mock_file_finish = mock_open(read_data=time_finish)
    with patch("builtins.open") as mock_open_func:
        mock_open_func.side_effect = [mock_file_start.return_value, mock_file_finish.return_value]
        result = drivers_best_lap("path_to_start_file", "path_to_end_file")
        assert result == expected_data


def test_drivers_best_lap_invalid_data():
    time_start = "SVF2018-05-24_12:02:58.917\nHNV2018-05-24_12:02:49.914"
    time_finish = "SVF2018-05-24_12:04:03.332\nNNV2018-05-24_12:04:02.979"
    mock_file_start = mock_open(read_data=time_start)
    mock_file_finish = mock_open(read_data=time_finish)

    with patch("builtins.open") as mock_open_func:
        mock_open_func.side_effect = [mock_file_start.return_value, mock_file_finish.return_value]

        with pytest.raises(ValueError):
            drivers_best_lap("path_to_start_file", "path_to_end_file")


def test_build_report_valid_data():
    drivers_abbr = param_for_abbr_decoder

    drivers_best_lap = param_for_drivers_best_lap

    expected_data = {
    'Sebastian Vettel': {
        'team': 'FERRARI',
        'best_lap': '0:01:04.415',
        'place': 1,
        'abbr': 'SVF'
    },
    'Kimi Raikkonen': {
        'team': 'FERRARI',
        'best_lap': '0:01:12.434',
        'place': 2,
        'abbr': 'KRF'
    },
    'Valtteri Bottas': {
        'team': 'MERCEDES',
        'best_lap': '0:01:12.618',
        'place': 3,
        'abbr': 'VBM'
    }
}

    result = build_report(drivers_abbr, drivers_best_lap)
    assert result == expected_data
    

def test_build_report_empty_data():
    drivers_abbr = {}
    drivers_best_lap = {}
    expected_data = {}

    result = build_report(drivers_abbr, drivers_best_lap)
    assert result == expected_data


def test_build_report_keyerror():
    drivers_abbr = {"KRF":
                    {"name": "Kimi Räikkönen",
                     "team": "FERRARI"},
                    "SVF":
                    {"name": "Sebastian Vettel",
                     "team": "FERRARI"},
                    }
    drivers_best_lap = {"SVF": "0:01:04.415",
                        "KRF": "0:01:12.434",
                        "VBM": "0:01:12.618",
                        }

    with pytest.raises(KeyError):
        build_report(drivers_abbr, drivers_best_lap)
