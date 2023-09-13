import salabim as sim

class Movement(sim.Component):
    moving_amount = None
    interval = None
    system = None

    def setup(self, moving_amount, interval, system):
        self.moving_amount = moving_amount
        self.interval = interval
        self.system = system


    def process(self):
        self.hold(till=9*60*60)
        
        while self.system.env.now() < 17*60*60:
            movable_employees = [] #assuming employees have fix schedule
            for floor in self.system.floors:
                movable_employees += floor.idle_queue

            moving_employees = sim.random.sample(movable_employees, min(self.moving_amount, len(movable_employees)))
            for e in moving_employees:
                e.destination = sim.IntUniform(1, self.system.floor_amount-1).sample()
                e.activate()
            
            self.hold(self.interval)
        
        for e in self.system.employees:
            e.hold(till=e.departure_time)
