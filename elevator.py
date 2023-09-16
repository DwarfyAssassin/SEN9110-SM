import salabim as sim
import numpy as np

class Elevator(sim.Component):
    holding_queue = None
    capacity = None
    travel_speed = None # second/floor
    deceleration_time = None
    acceleration_time = None
    loading_time = None
    unloading_time = None
    location = None # floor number
    destination = None
    is_moving = None
    system = None


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


    def process(self):
        while True:
            while self.destination == -1:
                for e in self.holding_queue:
                    if self.destination == -1 or (abs(e.destination - self.location) > abs(self.destination - self.location)):
                        self.destination = e.destination
                if self.destination == -1:
                    for floor in self.system.floors:
                        if floor.elevator_queue_up.length() > 0 or floor.elevator_queue_down.length() > 0:
                            if self.destination == -1 or abs(floor.number - self.location) > abs(self.destination - self.location):
                                self.destination = floor.number
                
                if self.destination == -1:
                    self.standby()
            

            # leave people
            for e in self.holding_queue:
                if e.destination == self.location:
                    self.stop_moving()

                    e.leave(self.holding_queue)
                    e.enter(self.system.floors[self.location].idle_queue)
                    e.location = self.location
                    self.hold(self.unloading_time.sample())

            # enter people down
            if self.location >= self.destination and self.system.floors[self.location].elevator_queue_down.length() > 0:
                self.stop_moving()
                
                for i in range(min(self.capacity - self.holding_queue.length(), self.system.floors[self.location].elevator_queue_down.length())):
                    e = self.system.floors[self.location].elevator_queue_down.pop()
                    e.enter(self.holding_queue)
                    self.hold(self.loading_time.sample())
            
            # enter people up
            if self.location <= self.destination and self.system.floors[self.location].elevator_queue_up.length() > 0:
                self.stop_moving()

                for i in range(min(self.capacity - self.holding_queue.length(), self.system.floors[self.location].elevator_queue_up.length())):
                    e = self.system.floors[self.location].elevator_queue_up.pop()
                    e.enter(self.holding_queue)
                    self.hold(self.loading_time.sample())



            # if destination => destination = -1 else move floors
            if self.location == self.destination:
                self.destination = -1
            else:
                self.start_moving()
                self.location += np.sign(self.destination - self.location)
                self.hold(self.travel_speed)

    def stop_moving(self):
        if self.is_moving:
            self.is_moving = False
            self.hold(self.deceleration_time)

    def start_moving(self):
        if not self.is_moving:
            self.is_moving = True
            self.hold(self.acceleration_time)