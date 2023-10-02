import salabim as sim

from components.person import Person

class Visitor(Person):
    def setup(self, arrival_time, departure_time, destination, system):
        super().setup(arrival_time, departure_time, destination, system)
        self.takes_stairs = False
        self.move_floors = False
        self.departure_time = sim.Uniform(self.arrival_time, 17.5 * 60 * 60).sample()

    def get_animation_color(self):
        return "green"