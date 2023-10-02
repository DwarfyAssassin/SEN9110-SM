import salabim as sim

class Floor(sim.Component):
    elevator_queue_up:sim.Queue = None
    elevator_queue_down:sim.Queue = None
    idle_queue:sim.Queue = None
    number:int = None

    def setup(self, number):
        self.elevator_queue_up = sim.Queue(self.name() + "-elevator_queue_up")
        self.elevator_queue_down = sim.Queue(self.name() + "-elevator_queue_down")
        self.idle_queue = sim.Queue(self.name() + "-idle_queue")
        self.number = number

        sim.AnimateRectangle((400, 70*self.number + 258, 522, 70*self.number + 282), text="", fillcolor="50%gray", arg=self)
        sim.AnimateQueue(self.elevator_queue_down, x=500, y=70*self.number + 260, title=f"", direction="w", id="down")
        
        sim.AnimateRectangle((400, 70*self.number + 288, 522, 70*self.number + 312), text="", fillcolor="50%gray", arg=self)
        sim.AnimateQueue(self.elevator_queue_up, x=500, y=70*self.number + 290, title=f"", direction="w", id="up")

        sim.AnimateRectangle((20, 70*self.number + 273, 392, 70*self.number + 297), text="", fillcolor="50%gray", arg=self)
        sim.AnimateQueue(self.idle_queue, x=370, y=70*self.number + 275, title=f"Floor {number} queues", direction="w", id="idle")