import simpy
import random
import statistics

# -----------------------------
# SIMULATION PARAMETERS
# -----------------------------
RANDOM_SEED = 42
SIM_TIME = 480  # minutes (8 hours)
EMPLOYEE_COUNT = 3
IN_HOURS = SIM_TIME/60

# Arrival rates (vehicles per minute)
ARRIVAL_RATE_NORMAL = 1 / 3
ARRIVAL_RATE_PEAK = 1 / 1.5

# Fuel probabilities
FUEL_PROB = {
    "petrol92": 0.7,
    "diesel": 0.25,
    "kerosene": 0.5
}

# Fueling times (minutes)
FUEL_TIME = {
    "petrol92": 0.75,
    "diesel": 4,
    "kerosene": 3
}

# Payment probabilities & times
PAYMENT_PROB = {"cash": 0.85, "card": 0.15}
PAYMENT_TIME = {"cash": 0.4, "card": 1}


# -----------------------------
# FUEL STATION RESOURCES
# -----------------------------
class FuelStation:
    def __init__(self, env, employees):
        self.env = env
        self.employee = simpy.Resource(env, capacity=employees)

        self.petrol92 = simpy.Resource(env, capacity=4)
        self.diesel = simpy.Resource(env, capacity=2)
        self.kerosene = simpy.Resource(env, capacity=2)


# -----------------------------
# VEHICLE PROCESS
# -----------------------------
def vehicle(env, name, station, fuel_type, results):
    arrival_time = env.now

    # Select dispenser
    dispenser = {
        "petrol92": station.petrol92,
        "diesel": station.diesel,
        "kerosene": station.kerosene
    }[fuel_type]

    # -------- Fuel Queue --------
    with dispenser.request() as disp_req:
        yield disp_req
        fuel_queue_wait = env.now - arrival_time
        results["fuel_wait"].append(fuel_queue_wait)

        fuel_time = random.expovariate(1 / FUEL_TIME[fuel_type])

        # -------- Payment + Fuel (Employee) --------
        with station.employee.request() as emp_req:
            pay_arrival = env.now
            yield emp_req
            payment_wait = env.now - pay_arrival

            payment_type = random.choices(
                list(PAYMENT_PROB.keys()),
                list(PAYMENT_PROB.values())
            )[0]

            pay_time = PAYMENT_TIME[payment_type]
            service_time = fuel_time + pay_time

            # Utilization tracking
            results["employee_busy"] += service_time
            results[f"{fuel_type}_busy"] += service_time
            results["payment_wait"].append(payment_wait)

            yield env.timeout(service_time)

    total_time = env.now - arrival_time
    results["system_time"].append(total_time)
    results["vehicles"] += 1


# -----------------------------
# VEHICLE GENERATOR
# -----------------------------
def generator(env, station, arrival_rate, results):
    i = 0
    while True:
        yield env.timeout(random.expovariate(arrival_rate))
        fuel_type = random.choices(
            list(FUEL_PROB.keys()),
            list(FUEL_PROB.values())
        )[0]
        i += 1
        env.process(vehicle(env, f"Vehicle-{i}", station, fuel_type, results))


# -----------------------------
# RUN SIMULATION
# -----------------------------
def run_simulation(peak=False):
    random.seed(RANDOM_SEED)
    env = simpy.Environment()

    arrival_rate = ARRIVAL_RATE_PEAK if peak else ARRIVAL_RATE_NORMAL
    station = FuelStation(env, EMPLOYEE_COUNT)

    results = {
        "fuel_wait": [],
        "payment_wait": [],
        "system_time": [],
        "vehicles": 0,
        "employee_busy": 0.0,
        "petrol92_busy": 0.0,
        "diesel_busy": 0.0,
        "kerosene_busy": 0.0
    }

    env.process(generator(env, station, arrival_rate, results))
    env.run(until=SIM_TIME)

    return results


# -----------------------------
# MAIN EXECUTION
# -----------------------------
if __name__ == "__main__":
    results = run_simulation(peak=False)
    
    print("\n----- PARAMETERS -----")
    print("Simulation Duration: ",SIM_TIME, "mins")
    print("Employees:", EMPLOYEE_COUNT)
    
    print("\n----- PERFORMANCE RESULTS -----")
    print("Vehicles Served:", results["vehicles"])
    print("Avg Fuel Queue Waiting Time:", round(statistics.mean(results["fuel_wait"]), 2), "min")
    print("Avg Payment Queue Waiting Time:", round(statistics.mean(results["payment_wait"]), 2), "min")
    print("Avg System Time:", round(statistics.mean(results["system_time"]), 2), "min")

    print("\n----- UTILIZATION -----")
    print("Employee Utilization:", round(results["employee_busy"] / (SIM_TIME * EMPLOYEE_COUNT), 2))
    print("Petrol92 Utilization:", round(results["petrol92_busy"] / (SIM_TIME * 4), 2))
    print("Diesel Utilization:", round(results["diesel_busy"] / (SIM_TIME * 2), 2))
    print("Kerosene Utilization:", round(results["kerosene_busy"] / (SIM_TIME * 2), 2))
