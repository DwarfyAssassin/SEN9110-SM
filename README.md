# README: Assignment 3

Created by: SEN9110 Simulation Masterclass, Group 12 

|                  Name                  |
|:--------------------------------------:|
| Chatarina Petra Salim, Chatarina Petra | 
|    Zelin, Almira Dilis Eliana Zelin    | 
|           Dutruel, Florentin           | 
|           Hui Yi, Yi           |


## Introduction

The repository contains simulation of employees and visitors using the elevator in a building. The model was built using Salabim.

## Getting Started

To run the simulation, you will need to have Python 3.11 or higher installed, as well as the Salabim, NumPy, and matplotlib libraries. You can install these dependencies using pip, the Python package manager:
```
    pip install -r requirements.txt
```
Once you have installed the necessary dependencies, you can launch the model and run the simulation by executing the main.py script:
```
    python main.py
```
The simulation will run from 8:00 to 18:00, with a second artificial time step. which is equivalent to 10 hours. 

### Output
During the simulation, the program will show animation of the elevator simulation. After the simulation has completed, the console will show brief statistics about mean idle time and occupancy rate of the elevator. In addition, a pop-up figure of the Queue Length and Queue Length of Service will be shown.

### Folder structure

This folder contains following files.
Before trying to run the model, please have a look at the _Getting Started_ section in this "README.md" file.

```

├─ components/
│  ├─ elevator.py           <- Process of elevator object.
│  ├─ elevatorcontroler.py  <- The decision maker of the elevator.
│  ├─ employee.py           <- Inheritance of the person class. Process of the employee to move between floors.
│  ├─ floor.py              <- Floor object.
│  ├─ mover.py              <- Process the triggered of employee movement between floor and departure.
│  ├─ person.py             <- The composition of employee and visitor.
│  ├─ visitor.py            <- Inheritance of person class. Elaborate the process of visitor lifecycle.
├─ .gitignore
├─ main.py                  <- Simulator of the elevator model.
├─ README.md                <- This file.
├─ requirements.txt         <- The requirements file for reproducing the analysis environment.
├─ reports/                 <- This folder contain our report in powerpoint format.

```

### Acknowledgments
This simulation was created as part of a group assignment of SEN9110 Simulation Masterclass.