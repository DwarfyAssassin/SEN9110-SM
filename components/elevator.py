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
        self.start_empty_time = -1
        self.empty_time = 0
        self.location_monitor = sim.Monitor("Location of " + self.name(), type="uint8", env=self.env, level=True, initial_tally=0)
        
        sim.AnimateRectangle((528+30*self.sequence_number(), 50, 552+30*self.sequence_number(), 238), text="", fillcolor="50%gray", arg=self)
        sim.AnimateQueue(self.holding_queue, x=530+30*self.sequence_number(), y=216, title="", direction="s", id="elevator")

        sim.AnimateRectangle((530+30*self.sequence_number(), 260, 550+30*self.sequence_number(), 310), y=lambda e, t: e.location*70, text=f"E{self.sequence_number()}", textcolor="black", fillcolor="blue", arg=self)
        
        sim.AnimateText(lambda: self.animation_idle_text(), x=600, y=400 - 120*self.sequence_number(), arg=self)
        sim.AnimateRectangle(lambda: self.animation_bar_size("full"), text="Full", fillcolor="green")
        sim.AnimateRectangle(lambda: self.animation_bar_size("idle"), text="Idle", fillcolor="red")
        sim.AnimateRectangle(lambda: self.animation_bar_size("empty"), text="Empty", fillcolor="blue")


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

                    if self.holding_queue.length() == 0:
                        self.start_empty_time = self.env.now()

                    self.hold(self.unloading_time.sample())

            # enter people down
            if self.location >= self.destination and self.system.floors[self.location].elevator_queue_down.length() > 0:
                self.stop_moving()
                
                while self.capacity - self.holding_queue.length() > 0 and self.system.floors[self.location].elevator_queue_down.length() > 0:
                    p = self.system.floors[self.location].elevator_queue_down.pop()
                    p.enter(self.holding_queue)

                    if self.start_empty_time != -1:
                        self.empty_time += self.system.env.now() - self.start_empty_time
                        self.start_empty_time = -1

                    self.hold(self.loading_time.sample())
            
            # enter people up
            if self.location <= self.destination and self.system.floors[self.location].elevator_queue_up.length() > 0:
                self.stop_moving()
 
                while self.capacity - self.holding_queue.length() > 0 and self.system.floors[self.location].elevator_queue_up.length() > 0:
                    p = self.system.floors[self.location].elevator_queue_up.pop()
                    p.enter(self.holding_queue)

                    if self.start_empty_time != -1:
                        self.empty_time += self.system.env.now() - self.start_empty_time
                        self.start_empty_time = -1

                    self.hold(self.loading_time.sample())


            # if at destination then -1 else move floors
            if self.location == self.destination:
                self.stop_moving()
                self.destination = -1
                self.start_idle_time = self.system.env.now()
                if self.start_empty_time != -1:
                    self.empty_time += self.system.env.now() - self.start_empty_time
                    self.start_empty_time = -1

                self.passivate()
            else:
                self.start_moving()
                self.location += np.sign(self.destination - self.location)
                self.hold(self.travel_speed)
                self.location_monitor.tally(self.location)


    def stop_moving(self):
        if self.is_moving:
            self.is_moving = False
            self.hold(self.deceleration_time)

    def start_moving(self):
        if not self.is_moving:
            self.is_moving = True
            self.hold(self.acceleration_time)


    def animation_idle_text(self):
        idle = self.idle_time
        if self.start_idle_time != -1:
            idle += self.system.env.now() - self.start_idle_time
        empty = self.empty_time
        if self.start_empty_time != -1:
            empty += self.system.env.now() - self.start_empty_time
        
        return f"Occupancy time and rate elevator {self.sequence_number()}:\nActive full {self.env.now() - empty - idle - 8*60*60:.0f}s\nActive empty {empty:.0f}s\nIdle {idle:.0f}s"
    
    def animation_bar_size(self, type):
        idle = self.idle_time
        if self.start_idle_time != -1:
            idle += self.system.env.now() - self.start_idle_time
        empty = self.empty_time
        if self.start_empty_time != -1:
            empty += self.system.env.now() - self.start_empty_time
        full = self.env.now() - empty - idle - 8*60*60
        total = idle + empty + full

        if total == 0: return (0,0,0,0)
        
        idle_p = idle/total
        empty_p = empty/total
        full_p = full/total

        if type == "idle":
            return (600, 370 - 120*self.sequence_number(), 600 + 400*idle_p, 395 - 120*self.sequence_number())
        if type == "empty":
            return (600 + 400*(idle_p), 370 - 120*self.sequence_number(), 600 + 400*(idle_p + empty_p), 395 - 120*self.sequence_number())
        if type == "full":
            return (600 + 400*(idle_p + empty_p), 370 - 120*self.sequence_number(), 1000, 395 - 120*self.sequence_number())
    