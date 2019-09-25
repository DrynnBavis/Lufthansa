import random
import numpy as np
import matplotlib.pyplot as plt
from queue import Queue

# Question 1 - random number generator
def get_exp_rand(rate_param):
    ran = random.random()
    lam = rate_param
    return -(1/lam)*np.log(1 - ran)

# 
def build_events(type, lam):
    time = get_exp_rand(lam)
    events = []
    while time < 1000:
        events.append((time, type))
        time += get_exp_rand(lam)
    return events

# Question 3 - Simulation
def simulate(rho):
    L = 2000 # average packet length (bits)
    C = 1000000 # transmission rate (1Mbits/s)
    lam = rho * C / L
    arrivals = build_events('a', lam)
    observes = build_events('o', 5*lam)
    events = sorted(arrivals + observes, key=lambda x: x[0])
    event_queue = Queue()
    [event_queue.put(i) for i in events]

    departures_waiting = 0
    departures_waiting_log = []
    active_departure = False
    events_processed = 0
    departure_time = 100000 #bigger than possible to indicate idle

    # begin simulation
    print("beginning simulation for {0} events".format(len(events)))
    while(not event_queue.empty()):
        # get event
        e = event_queue.get()

        # does event happen before next departure?
        if departure_time <= e[0]:
            if departures_waiting > 0:
                # queue next departure event
                departures_waiting -= 1
                xTime = get_exp_rand(1/L) / C
                departure_time = e[0] + xTime
            else:
                # empty queue, set to idle
                departure_time = 100000
        events_processed += 1

        # now handle event
        if (e[1] == 'a'):
            # arrival event
            if departures_waiting > 0 or departure_time < 100000:
                # currently servicing a departure, add to queue
                departures_waiting += 1
            else: 
                # empty queue, we can service it now
                xTime = get_exp_rand(1/L) / C
                departure_time = e[0] + xTime      
        else:
            # observation event
            departures_waiting_log.append(departures_waiting)

    return departures_waiting_log

def main():
    # get simulation data for rho = 0.25 -> 0.95
    graph_data = []
    for i in range(8):
        rho = 0.25 + i*0.10
        print("Starting rho = {0}".format(rho))
        results = simulate(rho)
        average_waiting_events = sum(results)/len(results)
        average_idle_proportion = results.count(0)/len(results)
        graph_data.append((rho, average_waiting_events, average_idle_proportion))
        print("Complete. Avg waiting departures: {0}, Idle proportion: {1}".format(average_waiting_events, average_idle_proportion))

    # plot it
    plt.scatter(*zip(*graph_data))
    plt.show()

if __name__ == "__main__":
    main()