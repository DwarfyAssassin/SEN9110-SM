import salabim as sim
from datetime import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
from elevator import Elevator
from employee import Employee

from floor import Floor
from movement import Movement


class System():
    floor_amount = 4

    
    floors = None
    employees = None
    elevators = None
    mover = None

    env = None
    
    def __init__(self, env):
        self.env = env
        self.floors = []
        self.employees = []
        self.elevators = []
        


if __name__ == "__main__":
    i_n = 1
    verboos = True 
    trace = False # open(file=".\output.txt", mode="w")
    
    
    for iteration in range(i_n):
        start_time = dt.now()

        env = sim.Environment(trace=trace, random_seed="*") # 1234567
        system = System(env)
        
        # Setup Building
        for i in range(system.floor_amount):
            system.floors.append(Floor(number = i))
        for i in range(1):
            system.elevators.append(Elevator(system = system))
        for i in range(100):
            system.employees.append(Employee(arrival_time = sim.Uniform(8 * 60 * 60, 9 * 60 * 60).sample(), 
                                             departure_time = sim.Uniform(17 * 60 * 60, 18 * 60 * 60).sample(),
                                             destination = sim.IntUniform(1, system.floor_amount-1).sample(),
                                             system = system))
        system.mover = Movement(moving_amount = 10,
                                interval = 1 * 60 * 60,
                                system = system)

  
        # Run
        env.run(till=18 * 60 * 60)
        end_time = dt.now()

        # for e in system.employees:
        #     print(f"{e.name()} - location {e.location} - destination {e.destination}")

        # Print Results
        if verboos: 
            print(f"Results in {end_time - start_time}s")

