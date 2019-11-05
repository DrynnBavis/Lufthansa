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
K_MAX = 10 #max number of retransmit attempts

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
    while time < 1000:
        time += get_exp_rand(lam)
        events.append(time)
    return events

def get_first_event_idx(time_queues):
    node_idx = -1
    current_time = 1000000000
    for i, q in enumerate(time_queues):
        if len(q) == 0:
            continue
        elif q[0] < current_time:
            node_idx = i
            current_time = q[0]
    return node_idx
    

# Main Questions ##############################################################

# Question 1 Demo
def simulate_csmacd(N, A, persistent):
    print("")
    print("Simulating CSMA/CD for N = {0}, A = {1}".format(N, A))
    # Setup the arrival queues
    packet_arrivals = [build_events(A) for i in range(N)]
    arrival_queues = []
    for arrival_list in packet_arrivals: #just converting lists to queues for performance
        event_queue = deque()
        event_queue.extend(arrival_list)
        arrival_queues.append(event_queue)

    # Initialise some structs
    k_dict = {} #dict of retry attempts 'k'
    for i in range(N):
        k_dict[i] = 0
    transmitted_packets = 0
    dropped_packets     = 0
    retransmit_attempts = 0
    packets_remaining   = 0
    for queue in arrival_queues:
        packets_remaining += len(queue) 
    print(packets_remaining)

    # Simulate
    while(packets_remaining):
        # find the first node we'll service
        node_idx = get_first_event_idx(arrival_queues)
        current_time = arrival_queues[node_idx][0]

        # detect collisions for this transmission
        collisions = []
        for i in range(N):
            if i == node_idx or len(arrival_queues[i]) == 0:
                continue # skip self and empty queues
            hops = abs(node_idx-i)
            t_prop = hops * D / S
            t_trans = L / R
            
            # Case 1: node i arrival occurs before bus is sensed to be busy -> collision
            if arrival_queues[i][0] <= current_time + t_prop:
                collisions.append(i)
                    
            # Case 2: bus is sensed to be busy -> add wait time to avoid collision
            elif arrival_queues[i][0] <= current_time + t_prop + t_trans:
                j = 0
                t_wait = current_time + t_prop + t_trans
                while (j < len(arrival_queues[i]) and arrival_queues[i][j] < t_wait):
                    arrival_queues[i][j] = t_wait
                    j += 1

            # Case 3: node i arrival is after the transmission, irrelevant
            else:
                continue

        # Handle collisions if they occured, else transmit was successful!
        if collisions:
            collisions.append(node_idx) # don't forget to add the transmitting node
            for collision_idx in collisions:
                hops = abs(node_idx-collision_idx)
                t_prop = hops * D / S
                k_dict[collision_idx] += 1
                if k_dict[collision_idx] <= K_MAX:
                    backoff_time = random.randint(1, (2**k_dict[collision_idx]) - 1) * 512 / R
                    j = 0
                    t_wait = current_time + t_prop + backoff_time
                    while (j < len(arrival_queues[collision_idx]) and arrival_queues[collision_idx][j] < t_wait):
                        arrival_queues[collision_idx][j] = t_wait
                        j += 1
                    retransmit_attempts += 1
                else:
                    k_dict[collision_idx] = 0
                    arrival_queues[collision_idx].popleft() #drop this packet
                    dropped_packets += 1
                    packets_remaining -= 1
        else:
            k_dict[node_idx] = 0
            arrival_queues[node_idx].popleft() # transmitted it, remove from queue
            transmitted_packets += 1
            packets_remaining -= 1

        # just some reporting of progress
        if packets_remaining % 100000 == 0:
            print(packets_remaining)
      
    # Print results
    total_transmits = transmitted_packets + dropped_packets + retransmit_attempts
    efficiency = transmitted_packets / total_transmits
    print("Efficiency = ", efficiency)
    print(transmitted_packets, dropped_packets)
    return efficiency




    
    


def question_one():
    A_list = [5, 12] # [7, 10, 20] # Poisson packet arrival rate
    N_list = [20, 40, 60, 80, 100] # num nodes on LAN

    data = {}
    for A in A_list:
        data[A] = []
        for N in N_list:
            results = (simulate_csmacd(N, A, True))
            data[A].append(results)
    
    plt.xlabel('Nodes in network (N)')
    plt.ylabel('Efficiency')
    plt.plot(data)
    plt.show()


def main():
    question_one()

if __name__ == "__main__":
    main()