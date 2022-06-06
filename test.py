class Person(object):
    species = "Human Being"

    def __init__(self, name):
        self.name = name 

    def __str__(self):
        return self.name

    def rename(self, renamed):
        self.rename = renamed
        print("Now my name is {self.name}")

kelly = Person("kelly")
saquib = Person("Saquib Mohiuddin Siddiqui")

print(saquib.name)