from multiprocessing import Pool

def addition(x):
    return x+x
def subtraction(x):
    return x-x

if __name__ == '__main__':

    # Define the dataset
    dataset = [1, 2, 3]

    # Output the dataset
    print ('Dataset: ' + str(dataset))

    # Run this with a pool of 5 agents having a chunksize of 3 until finished
    agents = 5
    chunksize = 3
    with Pool(processes=agents) as pool:
        result = pool.map(addition, dataset)

    # Output the result
    print ('Result:  ' + str(result))