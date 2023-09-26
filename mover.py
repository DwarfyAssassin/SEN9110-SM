import salabim as sim

class Mover(sim.Component):
    moving_amount:int = None
    interval:float = None
    system = None

    def setup(self, moving_amount, interval, system):
        self.moving_amount = moving_amount
        self.interval = interval
        self.system = system


    def process(self):
        self.hold(till=9*60*60)
        
        while self.system.env.now() < 17*60*60:
            # Find all eligible people to move
            movable_people = [] #assuming employees have fix schedule
            for floor in self.system.floors:
                movable_people += floor.idle_queue
            movable_people = [p for p in movable_people if p.move_floors]

            # Pick sample and set destination
            moving_people = sim.random.sample(movable_people, min(self.moving_amount, len(movable_people)))
            for p in moving_people:
                while p.destination == p.location:
                    p.destination = sim.IntUniform(1, self.system.floor_amount-1).sample()
                p.hold(sim.Uniform(0, 1 * 60 * 60 - 1).sample())
            
            self.hold(self.interval)