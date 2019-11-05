import random
import numpy as np
from collections import deque
import csv

# Given Variables
C = 3 * 10**8 #[m/sec] speed of light
D = 10 #[metres]
S = (2/3) * C #[m/sec] propagation speed
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

# Main Questions ##############################################################

# Question 1 Demo
def simulate_csmacd(N, A, persistent):
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
    wait_dict = {} #dict of wait time offsets per node
    for i in range(N):
        wait_dict[i] = 0
    transmitted_packets = 0
    dropped_packets = 0
    retransmit_attempts = 0

    # Simulate
    while(True):
        # find the first node we'll service
        node_idx = 0
        current_time = 1000
        for i, q in enumerate(arrival_queues):
            if len(q) and wait_dict[i] + q[0] < current_time:
                node_idx = i
                current_time = q[0]

        # detect collisions for this transmission
        collision = False
        for i in range(N):
            if i == node_idx: # skip self node
                continue
            hops = abs(node_idx-i)
            t_prop = hops * D / S
            t_trans = L / R
            
            # Case 1: node i arrival occurs before bus is sensed to be busy -> collision
            if wait_dict[i] + arrival_queues[i][0] < current_time + t_prop:
                collision = True
                k_dict[i] += 1
                if k_dict[i] <= K_MAX:
                    backoff_time = random.uniform(0, 2^k_dict[i] - 1) * 512 / R
                    wait_dict[i] += backoff_time
                    retransmit_attempts += 1
                else:
                    k_dict[i] = 0
                    arrival_queues[i].popleft() #drop this packet
                    dropped_packets += 1

            # Case 2: bus is sensed to be busy -> add wait time to avoid collision
            elif wait_dict[i] + arrival_queues[i][0] < current_time + t_prop + t_trans:
                t_wait = current_time + t_prop + t_trans - arrival_queues[i][0]
                wait_dict[i] += t_wait

            # Case 3: node i arrival is after the transmission, irrelevant
            else:
                continue
        
        if collision:
            k_dict[node_idx] += 1
            if k_dict[node_idx] <= K_MAX:
                backoff_time = random.uniform(0, 2^k_dict[node_idx] - 1) * 512 / R
                wait_dict[node_idx] += backoff_time
                retransmit_attempts += 1
            else:
                k_dict[node_idx] = 0
                arrival_queues[node_idx].popleft() #drop this packet from queue
                dropped_packets += 1
        else:
            arrival_queues[node_idx].popleft() # transmitted it, remove from queue
            transmitted_packets += 1



            





    
    


def question_one():
    A_list = [7, 10, 20] # Poisson packet arrival rate
    N_list = [20, 40, 60, 80, 100] # num nodes on LAN

    for A in A_list:
        for N in N_list:
            simulate_csmacd(N, A, True)

def main():
    question_one()

if __name__ == "__main__":
    main()