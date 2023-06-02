from peewee import SqliteDatabase, Model, CharField, TextField
from datetime import date


db = SqliteDatabase("test.db")

class Person(Model):
    name = CharField()
    birthday = TextField()
    
    class Meta:
        database = db
        table_name = "persons"
        
db.connect()
Person.create_table()


nazar = Person.create(name="Nazar", birthday=date(1995, 4, 24))
vetal = Person(name="Vilaii", birthday=date(1994, 12, 24)).save()
grandma = Person.create(name='Grandma', birthday=date(1935, 3, 1))
herb = Person.create(name='Herb', birthday=date(1950, 5, 5))

print(nazar)
print(vetal)

a = Person.get(id=1)
print(a.name)

lt_1995 = Person.select().order_by(Person.birthday.desc())
print([person.name for person in lt_1995])


d1940 = "1940-1-1"
d1994 = date(1995, 1, 1)

query = Person.select().where((Person.birthday > d1940) & (Person.birthday < d1994))

print([person.birthday for person in query])