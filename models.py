import os

from peewee import SqliteDatabase, Model, CharField, IntegerField
from dotenv import load_dotenv


load_dotenv()
db = SqliteDatabase(os.getenv("DB_PATH"))

class DriverModel(Model):
    place = IntegerField(primary_key=True)
    name = CharField(max_length=100)
    abbr = CharField(max_length=3)
    team = CharField(max_length=50)
    best_lap = CharField(max_length=20)
    
    class Meta:
        database = db
        table_name = "drivers"
        order_by = "place"
        
    def serialize_report(self):
        return {
            "name": self.name,
            "place": self.place,
            "team": self.team,
            "best_lap": self.best_lap,
            "abbr": self.abbr
        }
        
    def serialize_drivers(self):
        return {
            "name": self.name,
            "team": self.team,
        }
