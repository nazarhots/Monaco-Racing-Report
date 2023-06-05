from models import db, DriverModel
from logger.logger import create_report_logger


logger = create_report_logger()

def add_drivers_to_db(report: dict):
    """Add drivers information to the database. """
    if not DriverModel.table_exists():
        db.create_tables([DriverModel])
        logger.info("DriverModel table created")
    with db:
        for driver_name, driver in report.items():
            DriverModel(name=driver_name,
                        abbr=driver.get("abbr"),
                        team=driver.get("team"),
                        best_lap=driver.get("best_lap")).save()
            logger.info(f"Driver {driver_name} ({driver.get('abbr')}) added to DB")
