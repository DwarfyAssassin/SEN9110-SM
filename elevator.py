import salabim as sim

class Elevator(sim.Component):
    holding_queue = None
    capacity = None
    travel_speed = None # second/floor
    decelerator_time = None
    accelerator_time = None
    loading_time = None
    unloading_time = None
    location = None # floor number
    destination = None
    system = None


    def setup(self, system):
        self.holding_queue = sim.Queue(self.name() + "-holding_queue")
        self.capacity = 8
        self.travel_speed = 2
        self.decelerator_time = 1
        self.accelerator_time = 1
        self.loading_time = sim.Erlang(8, 4) # mu = 2, sigma = 0.5
        self.unloading_time = sim.Erlang(4, 4) # mu = 1, sigma = 0.25
        self.location = 0
        self.destination = -1
        self.system = system


    def process(self):
        prev_destination = 0

        while True:
            # is_idle = self.holding_queue.length() == 0
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
            
            stopped = False
            has_decelerated = False

            # leave people
            for e in self.holding_queue:
                if e.destination == self.location:
                    if not has_decelerated:
                        has_decelerated = True
                        self.hold(self.decelerator_time)

                    e.leave(self.holding_queue)
                    e.enter(self.system.floors[self.location].idle_queue)
                    e.location = self.location
                    stopped = True
                    self.hold(self.unloading_time.sample())

            # enter people down
            if self.location >= self.destination and self.system.floors[self.location].elevator_queue_down.length() > 0:
                if not has_decelerated and (prev_destination != self.location):
                    has_decelerated = True
                    self.hold(self.decelerator_time)
                stopped = True
                
                for i in range(min(self.capacity - self.holding_queue.length(), self.system.floors[self.location].elevator_queue_down.length())):
                    e = self.system.floors[self.location].elevator_queue_down.pop()
                    e.enter(self.holding_queue)
                    self.hold(self.loading_time.sample())
            
            # enter people up
            if self.location <= self.destination and self.system.floors[self.location].elevator_queue_up.length() > 0:
                if not has_decelerated and (prev_destination != self.location):
                    has_decelerated = True
                    self.hold(self.decelerator_time)
                stopped = True
                for i in range(min(self.capacity - self.holding_queue.length(), self.system.floors[self.location].elevator_queue_up.length())):
                    e = self.system.floors[self.location].elevator_queue_up.pop()
                    e.enter(self.holding_queue)
                    self.hold(self.loading_time.sample())


            # if any want to leave or enter => slowdown + speed up
            if stopped:
                self.hold(self.accelerator_time)

            # if destination => destination = -1 else move floors
            if self.location == self.destination:
                prev_destination = self.destination
                self.destination = -1
            else:
                if self.location < self.destination:
                    self.location += 1
                else:
                    self.location -= 1
                self.hold(self.travel_speed)