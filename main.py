import random
import numpy as np
import matplotlib.pyplot as plt

# Question 1 - random events
def getListOfRands(type, num):
    myList = []
    for x in range (num):
        ran = random.random()
        lam = 75
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
    L = 2000 #bits
    C = 1000000 #1Mbps
    row = L * lam / C
    events = buildEvents()
    departSize = 0
    queueSize = []
    eventsProcessed = 0
    activeDeparture = False

    # begin simulation
    while(events):
        e = events.pop(0)
        if (e[0] == "a"):
            # arrival event
            if departSize or activeDeparture:
                departSize += 1
                #print("added d to q, size of events: {0}", len(events))
            else: 
                # empty queue, we can service it now
                xTime = getRandSize(75) / C
                dTime = e[1] + xTime
                count = 0
                while(events[count][1] < dTime):
                    count += 1
                    if count == len(events):
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
                xTime = getRandSize(75) / C
                dTime = e[1] + xTime
                count = 0
                while(events[count][1] < dTime):
                    count += 1
                    if count == len(events):
                        break
                events.insert(count, ("d", dTime))
                activeDeparture = True
                #print("removed d from q, size of events: {0}", len(events))
            else:
                activeDeparture = False
        eventsProcessed += 1
        print("Events complete: {0}", eventsProcessed, end="\r")

    return queueSize

def main():
    # get simulation data
    results = simulate()
    print(results)
    # pull idle data from results
    result2 = [(y, x) for x, y in results]
    plt.scatter(*zip(*result2))
    plt.show()

    # plot the results
    # plt.plot([1, 2, 3, 4])
    # plt.ylabel('some numbers')
    # plt.show()



if __name__ == "__main__":
    main()