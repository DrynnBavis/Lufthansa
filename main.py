import random
import numpy as np
import matplotlib.pyplot as plt

# Question 1 - random events
def getListOfRands(type, num):
    myList = []
    for x in range (num):
        ran = random.random()
        lam = 75 # rate parameter
        val = -(1/lam)*np.log(1 - ran)
        myList.append((type, val))
    return myList

def getRandSize(L):
    ran = random.random()
    lam = 1/L
    val = -(1/lam)*np.log(1 - ran)
    return val

# Question 2 - DES
def buildEvents():
    arrivals = getListOfRands("a", 1000)
    observes = getListOfRands("o", 5000)
    events = sorted(arrivals + observes, key=lambda x: x[1])
    return events

# Question 3 - Simulation
def simulate():
    lam = 75
    L = 2000 # average packet length (bits)
    C = 1000000 # transmission rate (1Mbits/s)
    rho = L * lam / C # or just hard code this to be 0.95? This comes to be 0.15
    events = buildEvents()
    departSize = 0
    queueSize = []
    eventsProcessed = 0
    activeDeparture = False

    # begin simulation
    while(events):
        e = events.pop(0)
        print("popped: ", e)
        if (e[0] == "a"):
            # arrival event
            if departSize or activeDeparture:
                departSize += 1
            else: 
                # empty queue, we can service it now
                xTime = getRandSize(L) / C
                dTime = e[1] + xTime
                count = 0
                if (len(events) > 0):
                    while(events[count][1] < dTime):
                        count += 1
                        if count + 1 >= len(events):
                            break
                events.insert(count, ("d", dTime))
                activeDeparture = True
                
        elif (e[0] == "o"):
            # observation event
            queueSize.append((departSize,e[1]))
        else:
            # departure event
            if departSize:
                departSize -= 1
                xTime = getRandSize(L) / C
                dTime = e[1] + xTime
                count = 0
                if (len(events) > 0):
                    while(events[count][1] < dTime):
                        count += 1
                        if count + 1 >= len(events):
                            break
                events.insert(count, ("d", dTime))
                activeDeparture = True
            else:
                activeDeparture = False
        eventsProcessed += 1

    return queueSize

def main():
    # get simulation data
    results = simulate()
    # pull idle data from results
    result2 = [(y, x) for x, y in results]
    plt.scatter(*zip(*result2))
    plt.show()

if __name__ == "__main__":
    main()