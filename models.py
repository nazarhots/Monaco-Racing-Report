from peewee import SqliteDatabase, Model, CharField, IntegerField

db = SqliteDatabase("racing_report.db")

class DriverModel(Model):
    place = IntegerField(primary_key=True)
    name = CharField(max_length=100)
    abbr = CharField(max_length=3)
    team = CharField()
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
            "best_lap": self.best_lap
        }
        
    def serialize_drivers(self):
        return {
            "name": self.name,
            "team": self.team,
        }