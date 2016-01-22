import sys
import math
import numpy as np

evals = 0
budget = 0
dist = None

class Solution:
    def __init__(self, permutation):
        self.permutation = permutation
        self.fitness = sys.float_info.max

def read_data(filename):
    global dist
    lines = open(filename).readlines()
    coords = []
    for line in lines:
        if line[0].isdigit():
            no, x, y = line.strip().split(" ")
            coords.append((float(x), float(y)))
    num = len(coords)
    dist = np.zeros(num ** 2)
    dist.shape = (num, num)
    for i in range(num - 1):
        for j in range(1, num):
            dist[i][j] = math.sqrt((coords[i][0] - coords[j][0]) ** 2 + (coords[i][1] - coords[j][1]) ** 2)
    return num, dist

def evaluate(sol):
    global evals
    evals += 1
    sol.fitness = 0
    for i in range(len(sol.permutation) - 1):
        sol.fitness += dist[sol.permutation[i]][sol.permutation[i+1]]

def gen_neighbours(sol):
    neighbours = []
    i = 0
    while (i < len(sol.permutation) - 1 & evals < budget):
        new_order = np.copy(sol.permutation)
        temp = new_order[i]
        new_order[i] = new_order[i + 1]
        new_order[i + 1] = temp
      
        new_neighbour = Solution(new_order)
        evaluate(new_neighbour)
        neighbours.append(new_neighbour)
        i += 1
    return neighbours

def random_search(filename):
    global evals, budget
    num, dist = read_data(filename)
    best = None
    while(evals < budget):
        current = Solution(np.random.permutation(range(num)))
        evaluate(current)   
        if best == None or best.fitness > current.fitness:
            best = current
    return best
if __name__ == '__main__':
    budget = 30000
    sol = random_search(sys.argv[1])
    print(sol.fitness)
    # print(sol.permutation)
