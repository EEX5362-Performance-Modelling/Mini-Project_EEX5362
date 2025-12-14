# Real Time Fuel Station Simulation

## Overview

This program simulates how a fuel station works.
It shows how vehicles arrive, wait, take fuel, make payment, and leave.

The simulation is created using SimPy.
It is used to study waiting time, queue behavior, and resource usage.

## Simulation Time

- Total simulation time: 8 hours (480 minutes)

- Random seed is fixed for repeatable results.

## Arrival Rates

- Normal time: one vehicle every 3 minutes

- Peak time: one vehicle every 1.5 minutes

## Fuel Demand

- Petrol 92 → most vehicles

- Diesel → moderate

- Kerosene → very few vehicles

## Payment Methods

- Cash → faster

- Card → slower

Most customers use cash.

## Performance is measured by:

This program calculates,

- Number of vehicles served

- Average waiting time for fuel

- Average waiting time for payment

- Total time spent in the system

- Employee utilization

- Pump utilization for each fuel type

## Requirement
Before running the code, make sure you have Python installed.

You’ll also need the following Python libraries:

```bash
pip install simpy
```
## How to Run the Simulation

1. Download or clone this project folder.

2. Open the project in PyCharm or VS Code.

3. Open the Python file (Simulation.py).

4. Run the program.

5. At the end of the simulation, results such as total vehicles served and average waiting time will be displayed.


## Outputs

At the end of the simulation, the following metrics will appear

- Simulation Parameters

- Waiting time (Fuel, Payment, System)

- Utilization of Employees and Pumps