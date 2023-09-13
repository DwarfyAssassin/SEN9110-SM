import salabim as sim

class Employee(sim.Component):
    arrival_time = None
    departure_time = None
    destination = None
    location = None
    system = None

    def setup(self, arrival_time, departure_time, destination, system):
        self.arrival_time = arrival_time
        self.departure_time = departure_time
        self.destination = destination
        self.system = system
        self.location = 0


    def process(self):
        self.hold(till=self.arrival_time)
        self.enter(self.system.floors[self.location].idle_queue)

        while True:
            if self.system.env.now() >= self.departure_time:
                self.destination = 0

            if self.location == self.destination:
                self.passivate()
            else:
                self.leave(self.system.floors[self.location].idle_queue)
                if self.location > self.destination:
                    self.enter(self.system.floors[self.location].elevator_queue_down)
                else:
                    self.enter(self.system.floors[self.location].elevator_queue_up)
                self.passivate()