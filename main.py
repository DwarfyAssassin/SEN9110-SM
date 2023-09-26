import random
import sys
import salabim as sim
from datetime import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from elevator import Elevator
from employee import Employee

from floor import Floor
from mover import Mover
from visitor import Visitor
from elevatorcontroler import ElevatorControler

class System():
    floor_amount = None
    
    floors:list[Floor] = None
    employees:list[Employee] = None
    visitors:list[Visitor] = None
    elevators:list[Elevator] = None
    mover:Mover = None
    elevator_controler:ElevatorControler = None

    env:sim.Environment = None
    
    def __init__(self, env, floor_n):
        self.env = env
        self.floors = []
        self.employees = []
        self.visitors = []
        self.elevators = []
        self.floor_amount = floor_n
        

if __name__ == "__main__":
    i_n = 10
    verboos = True 
    trace = False # open(file=".\output.txt", mode="w")

    sim_time_start = 8*60*60
    sim_time_end = 18*60*60
    FLOOR_AMOUNT = 13
    ELEVATOR_AMOUNT = 2

    floor_stats = np.zeros((i_n, FLOOR_AMOUNT, 4))
    elevator_stats = np.zeros((i_n, ELEVATOR_AMOUNT))
    
    for iteration in range(i_n):
        start_time = dt.now()

        # Setup env and system
        seed = int(random.random() * (2**32 - 1))
        env = sim.Environment(trace=trace, random_seed=seed)
        if verboos: print(f"Starting with seed {seed} ({iteration+1}/{i_n})")
        system = System(env, FLOOR_AMOUNT)
        env._now = sim_time_start
        
        # Setup Components
        for i in range(system.floor_amount):
            system.floors.append(Floor(number = i))
        for i in range(ELEVATOR_AMOUNT):
            system.elevators.append(Elevator(system = system))
        for i in range(396):
            system.employees.append(Employee(arrival_time = sim.Uniform(8 * 60 * 60, 9 * 60 * 60).sample(),
                                             departure_time = sim.Uniform(17 * 60 * 60, 18 * 60 * 60).sample(),
                                             destination = sim.IntUniform(1, system.floor_amount-1).sample(),
                                             system = system))
        for i in range(180):
            system.visitors.append(Visitor(arrival_time = sim.Uniform(8.5 * 60 * 60, 17.5 * 60 * 60).sample(),
                                             departure_time = None,
                                             destination = sim.IntUniform(1, system.floor_amount-1).sample(),
                                             system = system))
        system.mover = Mover(moving_amount = 30,
                                interval = 1 * 60 * 60,
                                system = system)
        system.elevator_controler = ElevatorControler(system = system)

        # Run
        env.run(till=sim_time_end)
        end_time = dt.now()



        # Print Single sim Results
        if verboos: 
            print(f"Finished in {end_time - start_time}s ({iteration+1}/{i_n})")

            # for e in system.employees:
            #     print(f"{e.name()}, {e.location}, {e.destination}")
            # for e in system.visitors:
            #     print(f"{e.name()}, {e.location}, {e.destination}")

            
            # x, w = system.floors[0].elevator_queue_up.length._xweight()
            # x = np.array(x).astype(float)
            # xw = x * w

            # t = np.append([0], np.cumsum(w)[:-1]) + 28800
            # n = x[:-1]
            # for i in range(len(n)):
            #     plt.plot([t[i], t[i+1]], [n[i], n[i]], "b", label="Queue up F0 length")
            #     plt.plot(t[i+1], n[i], "b.", label="Queue up F0 entry/exit")

            # t0 = system.elevators[0].stats_loc_t + [64800]
            # l0 = np.array(system.elevators[0].stats_loc) + 0.1
            # t1 = system.elevators[1].stats_loc_t + [64800]
            # l1 = np.array(system.elevators[1].stats_loc) + 0.2
            # for i in range(len(l0)):
            #     plt.plot([t0[i], t0[i+1]], [l0[i], l0[i]], "k", label="Elevator 1 location")
            # for i in range(len(l1)):
            #     plt.plot([t1[i], t1[i+1]], [l1[i], l1[i]], "r", label="Elevator 2 location")

            # plt.xlabel("Time [s] (61200 = 17:00h)")
            # plt.ylabel("Floor location [-] / Queue Length [people]")
            # plt.yticks(range(0, 13))
            # plt.title("Elevator and Queue up F0 behavior")
            # handles, labels = plt.gca().get_legend_handles_labels()
            # by_label = dict(zip(labels, handles))
            # plt.legend(by_label.values(), by_label.keys())
            # plt.show()
            print()

            for i in range(len(system.elevators)):
                elevator_stats[iteration, i] = system.elevators[i].idle_time
            
            for f in system.floors:        
                floor_stats[iteration, f.number, 0] = f.elevator_queue_up.length.mean(ex0=True)
                floor_stats[iteration, f.number, 1] = f.elevator_queue_down.length.mean(ex0=True)
                floor_stats[iteration, f.number, 2] = f.elevator_queue_up.length_of_stay.mean(ex0=True)
                floor_stats[iteration, f.number, 3] = f.elevator_queue_down.length_of_stay.mean(ex0=True)

    # Print multi sim results
    if verboos:
        print(f"Elevator stats, mean idle time {elevator_stats.mean():.0f}s, occupancy rate {(sim_time_end-sim_time_start - elevator_stats.mean()) / (sim_time_end-sim_time_start) * 100:.1f}%")

        x_labels = []
        for i in range(FLOOR_AMOUNT * 2):
            if i <= 12:
                x_labels += [f"F{i%13} up"]
            else:
                x_labels += [f"F{i%13} down"]

        plt.subplot(121)
        floor_stats_l = np.nan_to_num(np.append(floor_stats[:, :, 0], floor_stats[:, :, 1], axis=1))
        plt.errorbar(range(1, FLOOR_AMOUNT * 2 + 1), floor_stats_l.mean(axis=0), yerr=1.96*floor_stats_l.std(axis=0), fmt=".", capsize=6)
        plt.boxplot(floor_stats_l)
        plt.xticks(range(1, FLOOR_AMOUNT * 2 + 1), labels=x_labels, rotation=45, ha='right')
        plt.ylabel("People [-]")
        plt.title("Average Queue Length (excluding empty queue)")
        plt.legend(handles=[mpatches.Patch(color='k', label='Percentile boxplot'), mpatches.Patch(color='C0', label='Mean confidence interval')])
        
        plt.subplot(122)
        floor_stats_t = np.nan_to_num(np.append(floor_stats[:, :, 2], floor_stats[:, :, 3], axis=1))
        plt.errorbar(range(1, FLOOR_AMOUNT * 2 + 1), floor_stats_t.mean(axis=0), yerr=1.96*floor_stats_t.std(axis=0), fmt=".", capsize=6)
        plt.boxplot(floor_stats_t)
        plt.ylim(bottom=0)
        plt.xticks(range(1, FLOOR_AMOUNT * 2 + 1), labels=x_labels, rotation=45, ha='right')
        plt.ylabel("Time [s]")
        plt.title("Average Queue Time")
        plt.legend(handles=[mpatches.Patch(color='k', label='Percentile boxplot'), mpatches.Patch(color='C0', label='Mean confidence interval')])
        
        plt.show()