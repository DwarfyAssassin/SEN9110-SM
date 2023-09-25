import salabim as sim

# from main import System

class Person(sim.Component):
    arrival_time:float = None
    departure_time:float = None
    destination:int = None
    location:int = None
    takes_stairs:bool = None
    move_floors:bool = None
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
                if self.is_in_floor_e_queue():
                    self.leave(self.get_floor_e_queue())
                    self.enter(self.system.floors[self.location].idle_queue)

                self.destination = 0
                if self.location == self.destination:
                    break

            if self.location == self.destination:
                self.hold(till=self.departure_time)
            else:
                current_floor = self.system.floors[self.location]
                if not self.is_in_elevator():
                    self.leave(current_floor.idle_queue)

                # TODO messes up with people going home slightly
                if self.takes_stairs and abs(self.destination - self.location) <= 2 and current_floor.elevator_queue_down.length() + current_floor.elevator_queue_up.length() >= 10:
                    distance = abs(self.destination - self.location)
                    self.hold(sim.Uniform(15*distance, 25*distance).sample())
                    self.enter(self.system.floors[self.destination].idle_queue)
                    self.location = self.destination
                elif self.location > self.destination and not self.is_in_elevator():
                    self.enter(current_floor.elevator_queue_down)
                elif not self.is_in_elevator():
                    self.enter(current_floor.elevator_queue_up)
                
                if self.system.env.now() >= self.departure_time:
                    self.passivate()
                else:
                    self.hold(till=self.departure_time)
    


    def is_in_elevator(self):
        for e in self.system.elevators:
            if self._member(e.holding_queue):
                return True
        return False
    
    def is_in_floor_e_queue(self):
        for f in self.system.floors:
            if self._member(f.elevator_queue_down) or self._member(f.elevator_queue_up):
                return True
        return False
    
    def get_floor_e_queue(self):
        for f in self.system.floors:
            if self._member(f.elevator_queue_down):
                return f.elevator_queue_down
            if self._member(f.elevator_queue_up):
                return f.elevator_queue_up
        return None