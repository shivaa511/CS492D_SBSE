import sys
import math
import random
from operator import attrgetter
import numpy as np
import argparse

evals = 0
budget = 0
num = None
dist = None
n2opt = None

class Solution:
    def __init__(self, permutation, random=False):
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
            dist[i][j] = math.sqrt((coords[i][0] - coords[j][0]) ** 2 \
                    + (coords[i][1] - coords[j][1]) ** 2)
    return num, dist

def generate():
    limit = dist.mean() - dist.std()
    candidates = list(range(num))
    path = []
    path.append(random.choice(candidates))
    candidates.remove(path[0])
    for i in range(num-1):
        random.shuffle(candidates)
        for j in candidates:
            if dist[i][j] <= limit:
                path.append(j)
                break
        if path[-1] != j:
            j = random.choice(candidates)
            path.append(j)
        candidates.remove(j)
    return Solution(np.array(path))

def evaluate(sol):
    global evals
    evals += 1
    sol.fitness = 0
    for i in range(len(sol.permutation) - 1):
        sol.fitness += dist[sol.permutation[i]][sol.permutation[i+1]]

class Crossover:
    def pmx(self, parent_a, parent_b):
        assert(len(parent_a.permutation) == len(parent_b.permutation))
        size = len(parent_a.permutation)

        cp1 = random.randrange(size)
        cp2 = random.randrange(size)
        while(cp2 == cp1):
            cp2 = random.randrange(size)

        if cp2 < cp1:
            cp1, cp2 = cp2, cp1

        map_a = {}
        map_b = {}
        
        child_a = Solution(parent_a.permutation)
        child_b = Solution(parent_b.permutation)
        for i in range(cp1, cp2 + 1):
            item_a = child_a.permutation[i]
            item_b = child_b.permutation[i]
            child_a.permutation[i] = item_b
            child_b.permutation[i] = item_a
            map_a[item_b] = item_a
            map_b[item_a] = item_b

        self.check_unmapped_items(child_a, map_a, cp1, cp2)
        self.check_unmapped_items(child_b, map_b, cp1, cp2)

        return child_a, child_b

    def check_unmapped_items(self, child, mapping, cp1, cp2):
        assert(cp1 < cp2)
        for i in range(len(child.permutation)):
            if i < cp1 or i > cp2:
                mapped = child.permutation[i]
                while(mapped in mapping):
                    mapped = mapping[mapped]
                child.permutation[i] = mapped
        return child
       
class Mutation:
    def mutate(self, solution):
        size = len(solution.permutation)

        mp1 = random.randrange(size)
        mp2 = random.randrange(size)
        while(mp2 == mp1):
            mp2 = random.randrange(size)
        solution.permutation[mp1], solution.permutation[mp2] \
                = solution.permutation[mp2], solution.permutation[mp1]
        return solution

    def best_2opt(self, solution):
        size = len(solution.permutation)
        path = solution.permutation.copy()
        evaluate(solution)
        for k in range(n2opt):
            for i in range(size-1):
                for j in range(i+2, size-1):
                    if dist[i][i+1] + dist[j][j+1] \
                            > dist[i][j] + dist[i+1][j+1]:
                                path[i+1], path[j] = path[j], path[i+1]
                temp_sol = Solution(path)
                evaluate(temp_sol)
                if solution.fitness < temp_sol.fitness:
                    path = solution.permutation.copy()
                else:
                    solution.permutation = path.copy()
                    solution.fitness = temp_sol.fitness
        return solution


class BinaryTournament:
    def select(self, population):
        i = random.randrange(len(population))
        j = random.randrange(len(population))
        while i == j:
           j = random.randrange(len(population))
        
        a = population[i]
        b = population[j]
        if a.fitness < b.fitness:
            return a
        else: 
            return b

def ga(num, pop_size, elitism_ratio, restart_after):

    population = []
    selection_op = BinaryTournament()
    crossover_op = Crossover()
    mutation_op = Mutation()
    hall_of_fame = []
    
    for i in range(pop_size):                      
        new_individual = generate()
        evaluate(new_individual)
        population.append(new_individual)
    
    current_best = Solution(np.random.permutation(range(num)))
    population = sorted(population, key=attrgetter('fitness'))
    
    generation = 0

    while evals < budget:
        nextgeneration = []
        nextgeneration.append(population[0])
        nextgeneration.append(population[pop_size - 1])

        # elitism
        cut_line = int(pop_size * elitism_ratio)
        population = population[:cut_line]
        
        while len(nextgeneration) < pop_size:
            parent_a = selection_op.select(population)
            parent_b = selection_op.select(population)
            child_a, child_b = crossover_op.pmx(parent_a, parent_b)
            child_a = mutation_op.best_2opt(child_a)
            child_b = mutation_op.best_2opt(child_b)
            
            evaluate(child_a)
            evaluate(child_b)

            nextgeneration.append(child_a)
            nextgeneration.append(child_b)

        improved = False
        population = sorted(nextgeneration, key=attrgetter('fitness'))
        best = population[0]
        if best.fitness < current_best.fitness:
            current_best = best
            improved = True
            # print current_best_str
            print("{:3d}, {:5.3f}, {:5.3f}, {:5.3f} [eval: {:6d}]"
                    .format(generation, best.fitness, 
                        population[1].fitness,
                        population[2].fitness, evals))

        # restart
        if restart_after:
            if improved:
                restart_gen = generation + restart_after
            elif generation >= restart_gen:
                # hall-of-fame
                hall_of_fame.append(current_best)
                # reinit
                population = []
                for i in range(pop_size):
                    new_individual = generate()
                    evaluate(new_individual)
                    population.append(new_individual)
                current_best = Solution(np.random.permutation(range(num)))
                population = sorted(population, key=attrgetter('fitness'))
                generation = 0
                continue

        generation += 1

    hall_of_fame.append(current_best)
    hall_of_fame = sorted(hall_of_fame, key=attrgetter('fitness'))
    return hall_of_fame[0]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str,
            help="input file that contains tsp data set")
    parser.add_argument("-p", "--population", type=int,
            dest="pop_size", default=100,
            help="population size")
    parser.add_argument("-f", "--fitness", type=int,
            dest="budget", default=10000,
            help="budget for fitness evalution")
    parser.add_argument("-e", "--elitism", type=float,
            dest="ratio", default=1,
            help="ratio of population will be used for crossover")
    parser.add_argument("-r", "--restart_after", type=int,
            dest="generation", default=0,
            help="restart if do not improve for N generation")
    parser.add_argument("-2", "--repeat_2opt", type=int,
            dest="n", default=3,
            help="restart if do not improve for N generation")
    args = parser.parse_args()

    budget = args.budget; n2opt = args.n
    num, dist = read_data(args.file)
    generate()
    sol = ga(num, args.pop_size, args.ratio, args.generation)
    print("")
    print(sol.permutation.tolist().__str__()[1:-1])
    print(sol.fitness)
