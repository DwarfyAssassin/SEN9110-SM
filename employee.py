import salabim as sim

from person import Person

# from main import System

class Employee(Person):

    def setup(self, arrival_time, departure_time, destination, system):
        super().setup(arrival_time, departure_time, destination, system)
        self.takes_stairs = True
        self.move_floors = True