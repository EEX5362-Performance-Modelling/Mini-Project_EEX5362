import simpy
import random
import statistics

# Simulation settings
SIM_TIME = 480        # minutes (8 hours)
RANDOM_SEED = 42

# Arrival rates (vehicles per minute)
ARRIVAL_RATE_NORMAL = 25 / 60
ARRIVAL_RATE_PEAK = 40 / 60

# Fuel type probabilities
FUEL_TYPES = {
    "petrol": 0.55,
    "diesel": 0.30,
    "kerosene": 0.15
}

# Mean fueling times (minutes)
FUEL_TIME = {
    "petrol": 2.0,
    "diesel": 2.2,
    "kerosene": 3.0
}

# Payment settings
PAYMENT_PROB = {
    "cash": 0.75,
    "card": 0.25
}

PAYMENT_TIME = {
    "cash": 0.5,
    "card": 2.0
}

class FuelStation:
    def __init__(self, env, employees=1):
        self.env = env

        # Dispensers (2 per pump)
        self.petrol = simpy.Resource(env, capacity=4)   # 2 pumps × 2 dispensers
        self.diesel = simpy.Resource(env, capacity=2)
        self.kerosene = simpy.Resource(env, capacity=2)

        # Employees (shared)
        self.employee = simpy.Resource(env, capacity=employees)

def vehicle(env, name, station, fuel_type, results):
    arrival_time = env.now

    # Select correct dispenser
    if fuel_type == "petrol":
        dispenser = station.petrol
    elif fuel_type == "diesel":
        dispenser = station.diesel
    else:
        dispenser = station.kerosene

    with dispenser.request() as disp_req, station.employee.request() as emp_req:
        yield disp_req & emp_req

        wait_time = env.now - arrival_time

        # Fueling time
        fuel_time = random.expovariate(1.0 / FUEL_TIME[fuel_type])

        # Payment type
        payment_type = random.choices(
            list(PAYMENT_PROB.keys()),
            list(PAYMENT_PROB.values())
        )[0]

        payment_time = PAYMENT_TIME[payment_type]

        service_time = fuel_time + payment_time

        yield env.timeout(service_time)

        results["waiting_times"].append(wait_time)
        results["service_times"].append(service_time)

def vehicle_generator(env, station, arrival_rate, results):
    count = 0
    while True:
        interarrival = random.expovariate(arrival_rate)
        yield env.timeout(interarrival)

        fuel_type = random.choices(
            list(FUEL_TYPES.keys()),
            list(FUEL_TYPES.values())
        )[0]

        count += 1
        env.process(vehicle(env, f"Vehicle {count}", station, fuel_type, results))

def run_simulation(employees=1, peak=False):
    random.seed(RANDOM_SEED)
    env = simpy.Environment()

    arrival_rate = ARRIVAL_RATE_PEAK if peak else ARRIVAL_RATE_NORMAL
    station = FuelStation(env, employees)

    results = {
        "waiting_times": [],
        "service_times": []
    }

    env.process(vehicle_generator(env, station, arrival_rate, results))
    env.run(until=SIM_TIME)

    return results

if __name__ == "__main__":
    results = run_simulation(employees=1, peak=True)

    print("Average Waiting Time:", statistics.mean(results["waiting_times"]))
    print("Average Service Time:", statistics.mean(results["service_times"]))
    print("Vehicles Served:", len(results["waiting_times"]))
