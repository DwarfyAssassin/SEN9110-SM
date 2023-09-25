import salabim as sim

class ElevatorControler(sim.Component):
    system = None
    


    def setup(self, system):
        self.system = system


    def process(self):
        while True:
            # both elevator moving
            # no one in floor queues
            # if all people in queues are assigned to elevator
            

            destinations_up = set()
            destinations_down = set()
            while True:
                for e in self.system.elevators:
                    for p in e.holding_queue:
                        if e.destination == -1 or (abs(p.destination - e.location) > abs(e.destination - e.location)):
                            e.destination = p.destination

                # print("here1")

                idle_elevator = False
                for e in self.system.elevators:
                    if e.destination == -1:
                        # print("here1.5", e, e.destination)
                        idle_elevator = True
                        break

                # print("here2", idle_elevator)
                
                if not idle_elevator:
                    self.standby()
                else:
                    for f in self.system.floors:
                        if f.elevator_queue_up.length() > 0:
                            destinations_up = destinations_up.union({f.number})
                        if f.elevator_queue_down.length() > 0:
                            destinations_down = destinations_down.union({f.number})
                    
                    # print("here3", destinations_up, destinations_down)

                    for e in self.system.elevators:
                        visit = set()
                        for i in range(min(e.location, e.destination), max(e.location, e.destination) + 1):
                            visit = visit.union({i})

                        
                        if e.location > e.destination:
                            destinations_down - visit
                        else:
                            destinations_up - visit
                    
                    # print("here4", destinations_up, destinations_down)
                            
                    if len(destinations_up) == 0 and len(destinations_down) == 0:
                        self.standby()
                    else:
                        break

            # print("here5", destinations_up, destinations_down)
            
            # find 1 idle elevator
            movable_elevators = []
            for e in self.system.elevators:
                if e.destination == -1:
                    movable_elevators += [e]
            # print("here6", movable_elevators)
            elevator = sim.random.sample(movable_elevators, 1)[0]
            # print("here7", elevator, elevator.destination)

            # assign elevator
            for i in destinations_up.union(destinations_down):
                if elevator.destination == -1 or abs(i - elevator.location) > abs(elevator.destination - elevator.location):
                    elevator.destination = i

            # print("here8", elevator, elevator.destination)

                

            
            # break_flag = False
            # while True:
            #     for e in self.system.elevators:
            #         if e.destination > -1:
            #             break_flag = True
            #             break
            #     if break_flag: break
            #     self.standby()

            
            # while self.destination == -1:
            #     for p in self.holding_queue:
            #         if self.destination == -1 or (abs(p.destination - self.location) > abs(self.destination - self.location)):
            #             self.destination = p.destination

                # if self.destination == -1:
                #     for floor in self.system.floors:
                #         if floor.elevator_queue_up.length() > 0 or floor.elevator_queue_down.length() > 0:
                #             if self.destination == -1 or abs(floor.number - self.location) > abs(self.destination - self.location):
                #                 self.destination = floor.number

                # if self.destination == -1:
                #     if self.start_idle_time == -1:
                #         self.start_idle_time = self.system.env.now()
                #     self.standby()