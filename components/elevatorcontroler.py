import salabim as sim

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import System

class ElevatorControler(sim.Component):
    system:'System' = None
    
    def setup(self, system):
        self.system = system

    def process(self):
        while True:
            destinations_up = set()
            destinations_down = set()
            while True:
                # assign destintion from people in elevator
                for e in self.system.elevators:
                    for p in e.holding_queue:
                        if e.destination == -1 or (abs(p.destination - e.location) > abs(e.destination - e.location)):
                            e.destination = p.destination

                # find idle elevator
                idle_elevator = False
                for e in self.system.elevators:
                    if e.destination == -1:
                        idle_elevator = True
                        break

                if not idle_elevator:
                    self.standby()
                else:
                    # Find all button pressed floors
                    for f in self.system.floors:
                        if f.elevator_queue_up.length() > 0:
                            destinations_up = destinations_up.union({f.number})
                        if f.elevator_queue_down.length() > 0:
                            destinations_down = destinations_down.union({f.number})
                    
                    # Removed assigned floors
                    for e in self.system.elevators:
                        visit = set()
                        for i in range(min(e.location, e.destination), max(e.location, e.destination) + 1):
                            visit = visit.union({i})
                        if e.location > e.destination:
                            destinations_down - visit
                        else:
                            destinations_up - visit

                    # Break loop if unassigned floors left  
                    if len(destinations_up) == 0 and len(destinations_down) == 0:
                        self.standby()
                    else:
                        break

            
            # find 1 idle elevator
            movable_elevators = []
            for e in self.system.elevators:
                if e.destination == -1:
                    movable_elevators.append(e)
            elevator = sim.random.sample(movable_elevators, 1)[0]

            # assign elevator
            for i in destinations_up.union(destinations_down):
                if elevator.destination == -1 or abs(i - elevator.location) > abs(elevator.destination - elevator.location):
                    elevator.destination = i
            elevator.activate()