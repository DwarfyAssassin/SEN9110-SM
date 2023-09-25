import salabim as sim

from employee import Employee

# from main import System

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
            movable_people = [] #assuming employees have fix schedule
            for floor in self.system.floors:
                movable_people += floor.idle_queue
            movable_people = [p for p in movable_people if p.move_floors]

            moving_people = sim.random.sample(movable_people, min(self.moving_amount, len(movable_people)))
            for e in moving_people:
                while e.destination == e.location:
                    e.destination = sim.IntUniform(1, self.system.floor_amount-1).sample()
                e.hold(sim.Uniform(0, 1 * 60 * 60 - 1).sample())
            
            self.hold(self.interval)