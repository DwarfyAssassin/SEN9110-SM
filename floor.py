import salabim as sim

class Floor(sim.Component):
    elevator_queue_up = None
    elevator_queue_down = None
    idle_queue = None
    number = None

    def setup(self, number):
        self.elevator_queue_up = sim.Queue(self.name() + "-elevator_queue_up")
        self.elevator_queue_down = sim.Queue(self.name() + "-elevator_queue_down")
        self.idle_queue = sim.Queue(self.name() + "-idle_queue")
        self.number = number


    # def process(self):
    #     while True: