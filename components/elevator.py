import salabim as sim
import numpy as np

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import System

class Elevator(sim.Component):
    holding_queue:sim.Queue = None
    capacity:int = None
    travel_speed:float = None # second/floor
    deceleration_time:float = None
    acceleration_time:float = None
    loading_time:sim.Erlang = None
    unloading_time:sim.Erlang = None
    location:int = None # floor number
    destination:int = None
    is_moving:bool = None
    system:'System' = None
    
    start_idle_time:float = None
    idle_time:float = None
    location_monitor:sim.Monitor = None
    stats_loc:list[float] = None
    stats_loc_t:list[float] = None


    def setup(self, system):
        self.holding_queue = sim.Queue(self.name() + "-holding_queue")
        self.capacity = 8
        self.travel_speed = 2
        self.deceleration_time = 1
        self.acceleration_time = 1
        self.loading_time = sim.Erlang(8, 4) # mu = 2, sigma = 0.5
        self.unloading_time = sim.Erlang(4, 4) # mu = 1, sigma = 0.25
        self.location = 0
        self.destination = -1
        self.is_moving = False
        self.system = system

        self.start_idle_time = -1
        self.idle_time = 0
        self.location_monitor = sim.Monitor("Location of " + self.name(), type="uint8", env=self.env, level=True, initial_tally=0)
        self.stats_loc = [0]
        self.stats_loc_t = [28800]


    def process(self):
        self.passivate()

        while True:
            # idle time stats
            if self.start_idle_time != -1:
                self.idle_time += self.system.env.now() - self.start_idle_time
                self.start_idle_time = -1

            # leave people
            for p in self.holding_queue:
                if p.destination == self.location:
                    self.stop_moving()
                    p.leave(self.holding_queue)
                    p.enter(self.system.floors[self.location].idle_queue)
                    p.location = self.location
                    self.hold(self.unloading_time.sample())

            # enter people down
            if self.location >= self.destination and self.system.floors[self.location].elevator_queue_down.length() > 0:
                self.stop_moving()
                
                while self.capacity - self.holding_queue.length() > 0 and self.system.floors[self.location].elevator_queue_down.length() > 0:
                    p = self.system.floors[self.location].elevator_queue_down.pop()
                    p.enter(self.holding_queue)
                    self.hold(self.loading_time.sample())
            
            # enter people up
            if self.location <= self.destination and self.system.floors[self.location].elevator_queue_up.length() > 0:
                self.stop_moving()
 
                while self.capacity - self.holding_queue.length() > 0 and self.system.floors[self.location].elevator_queue_up.length() > 0:
                    p = self.system.floors[self.location].elevator_queue_up.pop()
                    p.enter(self.holding_queue)
                    self.hold(self.loading_time.sample())


            # if at destination then -1 else move floors
            if self.location == self.destination:
                self.stop_moving()
                self.destination = -1
                self.start_idle_time = self.system.env.now()
                self.passivate()
            else:
                self.start_moving()
                self.location += np.sign(self.destination - self.location)
                self.hold(self.travel_speed)
                self.location_monitor.tally(self.location)

                self.stats_loc.append(self.location)
                self.stats_loc_t.append(self.system.env.now())


    def stop_moving(self):
        if self.is_moving:
            self.is_moving = False
            self.hold(self.deceleration_time)

    def start_moving(self):
        if not self.is_moving:
            self.is_moving = True
            self.hold(self.acceleration_time)