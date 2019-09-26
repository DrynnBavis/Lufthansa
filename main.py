import random
import numpy as np
from queue import Queue
import csv

# Helper Functions ############################################################

# Random number generator
def get_exp_rand(rate_param):
    ran = random.random()
    lam = rate_param
    return -(1/lam)*np.log(1 - ran)
    
# Event list builder
def build_events(type, lam):
    time = get_exp_rand(lam)
    events = []
    while time < 1000:
        events.append((time, type))
        time += get_exp_rand(lam)
    return events


# Main Questions ############################################################**

# Question 1 Demo
def question_one():
    rands = [get_exp_rand(75) for i in range (1000)]
    print("Question 1)")
    print("Variation: {0}".format(np.var(rands)))
    print("Mean: {0}".format(np.mean(rands)))

# Question 2 - M/M/1 Simulation Construction
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
                departure_time += xTime
            else:
                # empty queue, set to idle
                departure_time = 100000
        events_processed += 1

        # now handle event
        if (e[1] == 'a'):
            # arrival event
            departures_waiting += 1
            # do we have any departures yet?
            if departure_time == 100000:
                xTime = get_exp_rand(1/L) / C
                departure_time = e[0] + xTime
        else:
            # observation event
            departures_waiting_log.append(departures_waiting)

    return departures_waiting_log

# Question 3 Demo
def question_three():
    print("Question 3)")
    # get simulation data for rho = 0.25 -> 0.95
    result_data = []
    for i in range(8):
        rho = 0.25 + i*0.10
        print("Starting rho = {0}".format(rho))
        results = simulate(rho)
        average_waiting_events = sum(results)/len(results)
        average_idle_proportion = results.count(0)/len(results)
        result_data.append((rho, average_waiting_events, average_idle_proportion))
        print("Complete. Avg waiting departures: {0}, Idle proportion: {1}".format(average_waiting_events, average_idle_proportion))

    # done simulations, print results
    with open('SimulationResults_q3.csv','w') as out:
        csv.writer(out).writerows(result_data)

# Question 4 Demo
def question_four():
    print("Question 4)")
    results = simulate(1.2)
    average_waiting_events = sum(results)/len(results)
    average_idle_proportion = results.count(0)/len(results)
    print("Average waiting events: {0}".format(average_waiting_events))
    print("Average idle proportion: {1}".format(average_idle_proportion))

# Question 5 - M/M/1/K Simulation Construction
def simulate_k(rho, k):
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
    arrivals_dropped = 0
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
                departure_time += xTime
            else:
                # empty queue, set to idle
                departure_time = 100000
        events_processed += 1

        # now handle event
        if (e[1] == 'a'):
            # arrival event
            if departures_waiting == k:
                arrivals_dropped += 1
            else:
                departures_waiting += 1
            # do we have any departures yet?
            if departure_time == 100000:
                xTime = get_exp_rand(1/L) / C
                departure_time = e[0] + xTime
        else:
            # observation event
            departures_waiting_log.append(departures_waiting)

    p_loss = arrivals_dropped / len(arrivals)
    return (departures_waiting_log, p_loss)

# Question 6 Demo
def question_six():
    print("Question 6)")
    # get simulation data for k = 10, 25, 50 and then rho = 0.5 -> 1.5
    result_data = []
    for k in [10, 25, 50]:
        for i in range(11):
            rho = 0.5 + i*0.10
            print("Starting rho = {0}".format(rho))
            results, p_loss = simulate_k(rho,k)
            average_waiting_events = sum(results)/len(results)
            result_data.append((rho, k, average_waiting_events, p_loss))
            print("Complete. Avg waiting departures: {0}, p_loss: {1}".format(average_waiting_events, p_loss))

        # done simulations, print results
        with open('SimulationResults_q6.csv','w') as out:
            csv.writer(out).writerows(result_data)

def main():
    question_one()
    question_three()
    question_four()
    question_six()



if __name__ == "__main__":
    main()