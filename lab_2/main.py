import random
import numpy as np
from collections import deque
import csv
import matplotlib.pyplot as plt

# Given Variables
C = 3 * 10**8 #[m/sec] speed of light
S = (2/3) * C #[m/sec] propagation speed
D = 10 #[metres]
R = 1 * 10**6 #[bits/sec]
L = 1500 #[bits]
t_trans = L / R #[sec]
K_MAX = 10 #max number of retransmit attempts
SIMULATION_TIME = 1000 #[sec]

# Helper Functions ############################################################

# Random number generator
def get_exp_rand(rate_param):
    ran = random.random()
    lam = rate_param
    return -(1/lam)*np.log(1 - ran)
    
# Event list builder
def build_events(lam):
    events = []
    time = 0
    while time < SIMULATION_TIME:
        time += get_exp_rand(lam)
        events.append(time)
    return events

def get_first_event_idx(time_queues):
    node_idx = -1
    earliest_time = 1000000000
    for i, q in enumerate(time_queues):
        if len(q) != 0 and q[0] < earliest_time:
            node_idx = i
            earliest_time = q[0]
    return node_idx
    
# Main Questions ##############################################################

# Question 1 Demo
def simulate_csmacd(N, A, persistent):
    print("")
    print("Simulating CSMA/CD for N = {0}, A = {1}, Persistent = {2}".format(N, A, persistent))

    # Setup the arrival queues
    packet_arrivals = [build_events(A) for i in range(N)]
    arrival_queues = []
    for arrival_list in packet_arrivals: #just converting lists to queues for performance
        event_queue = deque()
        event_queue.extend(arrival_list)
        arrival_queues.append(event_queue)

    # Initialise some counters
    collision_k = {} #dict of collision retry attempts 'k'
    for i in range(N):
        collision_k[i] = 0
    sensing_k = {} #dict of sensing retry attempts 'k'
    for i in range(N):
        sensing_k[i] = 0
    transmit_attempts = 0
    dropped_packets   = 0
    sent_packets      = 0
    current_time      = 0

    # Simulate
    while(current_time < SIMULATION_TIME):
        # Find the first node we'll service
        sender_idx = get_first_event_idx(arrival_queues)
        current_time = arrival_queues[sender_idx][0]
        transmit_attempts += 1

        # Detect collisions for this transmission
        collisions = []
        for i in range(N):
            if i != sender_idx and len(arrival_queues[i]): #skip self and empty queues
                hops = abs(sender_idx-i)
                t_prop = hops * D / S

                # Case 1: node i arrival occurs before bus is sensed to be busy -> collision
                if arrival_queues[i][0] <= current_time + t_prop:
                    collisions.append(i)
                    transmit_attempts += 1
                        
                # Case 2: bus is sensed to be busy -> add wait time to avoid collision
                elif arrival_queues[i][0] <= current_time + t_prop + t_trans:
                    if persistent:
                        # simulate tight-polling by setting new time to the end of current transmission
                        arrival_queues[i][0] = current_time + t_prop + t_trans
                    if not persistent:
                        while len( arrival_queues[i]) and arrival_queues[i][0] <= current_time + t_prop + t_trans:
                            sensing_k[i] += 1
                            if sensing_k[i] <= K_MAX:
                                t_backoff = random.randint(1, 2**sensing_k[i] - 1) * (512 / R)
                                arrival_queues[i][0] += t_backoff
                            else:
                                t_dropped = arrival_queues[i].popleft() #drop this packet
                                sensing_k[i] = 0
                                collision_k[i] = 0
                                dropped_packets += 1
                                transmit_attempts += 1
                                if len(arrival_queues[i]) and arrival_queues[i][0] < t_dropped:
                                    arrival_queues[i][0] = t_dropped
                        

        # Handle collisions if they occured, 
        if collisions:
            collisions.append(sender_idx) # don't forget to add the transmitting node
            for collision_idx in collisions:
                collision_k[collision_idx] += 1
                if collision_k[collision_idx] <= K_MAX:
                    t_backoff = random.randint(1, 2**collision_k[collision_idx] - 1) * (512 / R)
                    arrival_queues[collision_idx][0] += t_backoff
                else:
                    t_dropped = arrival_queues[collision_idx].popleft()
                    sensing_k[collision_idx] = 0
                    collision_k[collision_idx] = 0
                    dropped_packets += 1
                     # if the next node in the queue arrives before current time, adjust it
                    if len(arrival_queues[collision_idx]) and arrival_queues[collision_idx][0] < t_dropped:
                        arrival_queues[collision_idx][0] = t_dropped

        else: # else transmit was successful!
            t_arrival = arrival_queues[sender_idx].popleft()
            sensing_k[i] = 0
            collision_k[i] = 0
            sent_packets += 1
            # if the next node in the queue arrives before we're done transmitting, adjust it
            if len(arrival_queues[sender_idx]) and arrival_queues[sender_idx][0] < t_arrival + t_trans:
                arrival_queues[sender_idx][0] = t_arrival + t_trans
        
      
    # Print results
    efficiency = sent_packets / transmit_attempts
    throughput = (sent_packets * L / SIMULATION_TIME)/R
    print("Efficiency =", efficiency)
    print("Throughput =", throughput)
    return (efficiency,throughput)

def main():
    A_list = [7, 10, 20] # Poisson packet arrival rate
    N_list = [20, 40, 60, 80, 100] # num nodes on LAN

    # Fetch data from simulations
    persis_eff = {}
    persis_thru = {}
    nonper_eff = {}
    nonper_thru = {}

    # Simulate some data
    for A in A_list:
        persis_eff[A] = []
        persis_thru[A] = []
        nonper_eff[A] = []
        nonper_thru[A] = []

        for N in N_list:
            eff, thru = simulate_csmacd(N, A, True)
            persis_eff[A].append(eff)
            persis_thru[A].append(thru)
            eff, thru = simulate_csmacd(N, A, False)
            nonper_eff[A].append(eff)
            nonper_thru[A].append(thru)

    # Plotting the data
    eff_styles = ['r', 'b', 'g']
    thru_styles = ['r--', 'b--', 'g--']

    plt.title('Efficiency of Persistent Medium Sensing', fontdict=None, loc='center')
    plt.xlabel('Nodes in network (N)')
    plt.ylabel('Efficiency')
    for idx, A in enumerate(A_list):
        plt.plot(N_list, persis_eff[A], eff_styles[idx], label="A = {0}".format(A))
    plt.legend(loc='upper right', shadow=False)
    plt.grid(True)
    plt.show()

    plt.title('Throughput of Persistent Medium Sensing', fontdict=None, loc='center')
    plt.xlabel('Nodes in network (N)')
    plt.ylabel('Throughput [Mbps]')
    for idx, A in enumerate(A_list):
        plt.plot(N_list, persis_thru[A], thru_styles[idx], label="A = {0}".format(A))
    plt.legend(loc='upper right', shadow=False)
    plt.grid(True)
    plt.show()

    plt.title('Efficiency of Non-Persistent Medium Sensing', fontdict=None, loc='center')
    plt.xlabel('Nodes in network (N)')
    plt.ylabel('Efficiency')
    for idx, A in enumerate(A_list):
        plt.plot(N_list, nonper_eff[A], eff_styles[idx], label="A = {0}".format(A))
    plt.legend(loc='upper right', shadow=False)
    plt.grid(True)
    plt.show()

    plt.title('Throughput of Non-Persistent Medium Sensing', fontdict=None, loc='center')
    plt.xlabel('Nodes in network (N)')
    plt.ylabel('Throughput [Mbps]')
    for idx, A in enumerate(A_list):
        plt.plot(N_list, nonper_thru[A], thru_styles[idx], label="A = {0}".format(A))
    plt.legend(loc='upper right', shadow=False)
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()