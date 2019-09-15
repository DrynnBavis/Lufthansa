import random
import numpy as np

def getListOfRands():
    myList = []
    for x in range (1000):
        ran = random.random()
        lam = 75
        val = -(1/lam)*np.log(1 - ran)
        myList.append(val)
    return myList

def main():
    rands = getListOfRands()
    variance = np.var(rands)
    mean = np.mean(rands)
    print("Variance: ", variance)
    print("mean: ", mean)

if __name__ == "__main__":
    main()