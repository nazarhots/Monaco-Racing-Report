from models import db, DriverModel


def add_drivers_to_db(report: dict):
    """Add drivers information to the database. """
    with db:
        for driver_name, driver in report.items():
            DriverModel(name=driver_name,
                        abbr=driver["abbr"],
                        team=driver["team"],
                        best_lap=driver["best_lap"]).save()
