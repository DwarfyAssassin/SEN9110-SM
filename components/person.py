import salabim as sim

from typing import TYPE_CHECKING, Any, Tuple

if TYPE_CHECKING:
    from main import System

class Person(sim.Component):
    arrival_time:float = None
    departure_time:float = None
    destination:int = None
    location:int = None
    takes_stairs:bool = None
    move_floors:bool = None
    system:'System' = None

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
            # If past departure time then set destination 0
            if self.system.env.now() >= self.departure_time:
                if self.is_in_floor_e_queue():
                    self.leave(self.get_floor_e_queue())
                    self.enter(self.system.floors[self.location].idle_queue)

                self.destination = 0
                if self.location == self.destination:
                    break
            
            # If at destination wait untill depature time
            if self.location == self.destination:
                self.hold(till=self.departure_time)
            else:
                current_floor = self.system.floors[self.location]
                if not self.is_in_elevator():
                    self.leave(current_floor.idle_queue)

                # Enter stairs or elevator to go to destination
                if self.takes_stairs and not self.is_in_elevator() and abs(self.destination - self.location) <= 2 and current_floor.elevator_queue_down.length() + current_floor.elevator_queue_up.length() >= 10:
                    distance = abs(self.destination - self.location)
                    self.hold(sim.Uniform(15*distance, 25*distance).sample())
                    self.enter(self.system.floors[self.destination].idle_queue)
                    self.location = self.destination
                elif self.location > self.destination and not self.is_in_elevator():
                    self.enter(current_floor.elevator_queue_down)
                elif not self.is_in_elevator():
                    self.enter(current_floor.elevator_queue_up)
                
                # Sleep until departure or end of sim
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
    
    def get_animation_color(self):
        return "red"
    
    def animation_objects(self, id: Any) -> Tuple:
        ar = sim.AnimateRectangle((0,0,20,20), text=str(self.sequence_number()), fillcolor=self.get_animation_color(), textcolor="white", arg=self)
        return 25, 25, ar