import salabim as sim
from datetime import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
from elevator import Elevator
from employee import Employee

from floor import Floor
from mover import Mover


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
    sim_time_start = 8*60*60
    sim_time_end = 18*60*60
    i_n = 10
    verboos = True 
    trace = False # open(file=".\output.txt", mode="w")
    floor_stats = np.zeros((i_n, 4, 4))
    elevator_stats = np.zeros(i_n)
    
    for iteration in range(i_n):
        start_time = dt.now()

        env = sim.Environment(trace=trace, random_seed="*") # 1234567
        system = System(env)
        env._now = sim_time_start
        
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
        system.mover = Mover(moving_amount = 10,
                                interval = 1 * 60 * 60,
                                system = system)

        # Run
        env.run(till=sim_time_end)
        end_time = dt.now()

        # Print Results
        if verboos: 
            print(f"Results in {end_time - start_time}s ({iteration+1}/{i_n})")
            elevator_stats[iteration] = system.elevators[0].idle_time
            for f in system.floors:                
                floor_stats[iteration, f.number, 0] = f.elevator_queue_up.length.mean()
                floor_stats[iteration, f.number, 1] = f.elevator_queue_down.length.mean()
                floor_stats[iteration, f.number, 2] = f.elevator_queue_up.length_of_stay.mean()
                floor_stats[iteration, f.number, 3] = f.elevator_queue_down.length_of_stay.mean()


    if verboos:
        print(f"Elevator stats, mean idle time {elevator_stats.mean():.0f}s, occupancy rate {(sim_time_end-sim_time_start - elevator_stats.mean()) / (sim_time_end-sim_time_start) * 100:.1f}%")

        # for f in system.floors:
            # print(f"Floor {f.number}")
            # print(f"{'l_up':8} {floor_stats[:, f.number, 0].mean():5.3f} ({floor_stats[:, f.number, 0].mean() - 1.96*floor_stats[:, f.number, 0].std():.3f}-{floor_stats[:, f.number, 0].mean() + 1.96*floor_stats[:, f.number, 0].std():.3f})")
            # print(f"{'l_down':8} {floor_stats[:, f.number, 1].mean():5.3f} ({floor_stats[:, f.number, 1].mean() - 1.96*floor_stats[:, f.number, 1].std():.3f}-{floor_stats[:, f.number, 1].mean() + 1.96*floor_stats[:, f.number, 1].std():.3f})")
            # print(f"{'los_up':8} {floor_stats[:, f.number, 2].mean():5.3f} ({floor_stats[:, f.number, 2].mean() - 1.96*floor_stats[:, f.number, 2].std():.3f}-{floor_stats[:, f.number, 2].mean() + 1.96*floor_stats[:, f.number, 2].std():.3f})")
            # print(f"{'los_down':8} {floor_stats[:, f.number, 3].mean():5.3f} ({floor_stats[:, f.number, 3].mean() - 1.96*floor_stats[:, f.number, 3].std():.3f}-{floor_stats[:, f.number, 3].mean() + 1.96*floor_stats[:, f.number, 3].std():.3f})")
            # print()

        plt.subplot(121)
        plt.boxplot(np.append(floor_stats[:, :, 0], floor_stats[:, :, 1], axis=1))
        plt.xticks(range(1, 9), labels=["F0 up", "F1 up", "F2 up", "F3 up", "F0 down", "F1 down", "F2 down", "F3 down"], rotation=45, ha='right')
        plt.ylabel("People [-]")
        plt.title("Queue Length")
        
        plt.subplot(122)
        plt.boxplot(np.append(floor_stats[:, :, 2], floor_stats[:, :, 3], axis=1))
        plt.xticks(range(1, 9), ["F0 up", "F1 up", "F2 up", "F3 up", "F0 down", "F1 down", "F2 down", "F3 down"], rotation=45, ha='right')
        plt.ylabel("Time [s]")
        plt.title("Queue Length of Service")

        plt.show()