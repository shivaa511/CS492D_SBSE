import sudoku, random, sys
from operator import attrgetter
import argparse

evals = 0
budget = 0
PUZZLE = None

def generate():
    return sudoku.solve(PUZZLE)

def evaluate(sol):
    global evals
    evals += 1
    sol.evaluate()

class Crossover:
    @classmethod
    def pmx(cls, parent_a, parent_b):
        size = len(parent_a.holes)

        cp1 = random.randrange(size)
        cp2 = random.randrange(size)
        while cp1 == cp2:
            cp2 = random.randrange(size)
        if cp1 > cp2:
            cp1, cp2 = cp2, cp1

        child_a = parent_a.copy()
        child_b = parent_b.copy()
        for i in range(cp1, cp2 + 1):
            item_a = child_a.holes[i]
            item_b = child_b.holes[i]
            child_a.holes[i] = item_a
            child_b.holes[i] = item_b
        return child_a, child_b

class Mutation:
    @classmethod
    def swap(cls, sol):
        size = len(sol.holes)

        while True:
            mp1 = random.randrange(size)
            mp2 = random.randrange(size)
            while mp1 == mp2:
                mp2 = random.randrange(size)
            
            sol.holes[mp1], sol.holes[mp2] \
                    = sol.holes[mp2], sol.holes[mp1]

            if sol.holes[mp1] in \
                    sol.problem.candidates[sol.problem.holes[mp1]] \
                    and sol.holes[mp2] in \
                    sol.problem.candidates[sol.problem.holes[mp2]]:
                        break

        return sol

    @classmethod
    def swap_neighbor(cls, sol):
        size = len(sol.holes)

        mp1 = random.randrange(size)
        mp1_neighbor = sudoku.neighbor(sol.problem.holes[mp1])
        mp1_neighbor.remove(sol.problem.holes[mp1])
        _mp2 = random.choice(mp1_neighbor)
        while _mp2 not in sol.problem.holes:
            _mp2 = random.choice(mp1_neighbor)
        mp2 = sol.problem.holes.index(_mp2)
        
        sol.holes[mp1], sol.holes[mp2] \
                = sol.holes[mp2], sol.holes[mp1]
        return sol

    @classmethod
    def resample(cls, sol):
        size = len(sol.holes)

        mp = random.randrange(size)
        sol.holes[mp] = random.choice(
                sol.problem.candidates[sol.problem.holes[mp]])
        return sol

    @classmethod
    def resample2(cls, sol):
        size = len(sol.holes)

        mp1 = random.randrange(size)
        mp2 = random.randrange(size)
        sol.holes[mp1] = random.choice(
                sol.problem.candidates[sol.problem.holes[mp1]])
        sol.holes[mp2] = random.choice(
                sol.problem.candidates[sol.problem.holes[mp2]])
        return sol

Mutation.mutate = Mutation.resample2

class BinaryTournament:
    @classmethod
    def select(self, population):
        size = len(population)

        i = random.randrange(size)
        j = random.randrange(size)
        while i == j:
            j = random.randrange(size)

        a = population[i]
        b = population[j]
        if a.fitness < b.fitness:
            return a
        else:
            return b

def ga(pop_size, elitism_ratio=1, restart_after=0):
    assert PUZZLE != None
    population = []
    selection_op = BinaryTournament()
    crossover_op = Crossover()
    mutation_op = Mutation()
    hall_of_fame = []

    for i in range(pop_size):
        new_individual = generate()
        evaluate(new_individual)
        population.append(new_individual)

    current_best = generate()
    population = sorted(population, key=attrgetter('fitness'))

    generation = 0

    while budget==0 or evals < budget:
        next_generation = []
        next_generation.append(population[0])
        next_generation.append(population[pop_size - 1])

        # elitism
        cut_line = int(pop_size * elitism_ratio)
        population = population[:cut_line]
        # for i in range(pop_size - cut_line):
        #     new_individual = sudoku.solve(problem)
        #     evaluate(new_individual)
        #     population.append(new_individual)

        while len(next_generation) < pop_size:
            parent_a = selection_op.select(population)
            parent_b = selection_op.select(population)
            child_a, child_b = crossover_op.pmx(parent_a, parent_b)
            if random.random() < 0.4:
                child_a = mutation_op.mutate(child_a)
            if random.random() < 0.4:
                child_b = mutation_op.mutate(child_b)

            evaluate(child_a)
            evaluate(child_b)

            next_generation.append(child_a)
            next_generation.append(child_b)

        improved = False
        population = sorted(next_generation, key=attrgetter('fitness'))
        best = population[0]
        if best.fitness < current_best.fitness:
            current_best = best
            improved = True
            print("{:4d}, {:2d}, {:2d}, {:2d} [evals: {:7d}]"
                    .format(generation, best.fitness,
                        population[1].fitness,
                        population[2].fitness, evals))

        if current_best.fitness == 0:
            break

        # restart
        if restart_after:
            if improved:
                restart_gen = generation + restart_after
            elif generation >= restart_gen:
                # hall-of-fame
                hall_of_fame.append(current_best)
                # reinit
                population = []
                if random.random() < 0.15:
                    for sol in hall_of_fame:
                        population.append(sol)
                for i in range(pop_size - len(population)):
                    new_individual = generate()
                    evaluate(new_individual)
                    population.append(new_individual)
                current_best = generate()
                population = sorted(population, key=attrgetter('fitness'))
                generation = 0
                continue

        ##### DEBUG
        # if generation % 500 == 0 and generation != 0:
        #     print("{:4d}, {:2d}, {:2d}, {:2d} [evals: {:7d}]"
        #             .format(generation, best.fitness,
        #                 population[1].fitness,
        #                 population[2].fitness, evals))
        #     if generation % 3000 == 0:
        #         for sol in population[::10]:
        #             print(sol)
        #             print(sol.fitness)
        #             print('\n')
        ##### DEBUG END
        generation += 1
    
    hall_of_fame.append(current_best)
    hall_of_fame = sorted(hall_of_fame, key=attrgetter('fitness'))
    return hall_of_fame[0]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str,
            help="input file that contains sudoku puzzle")
    parser.add_argument("-p", "--population", type=int,
            dest="pop_size", default=1000,
            help="population size")
    parser.add_argument("-f", "--fitness", type=int,
            dest="budget", default=0,
            help="budget for fitness evalution [0: infinite]")
    parser.add_argument("-e", "--elitism", type=float,
            dest="ratio", default=1,
            help="ratio of population will be used for crossover")
    parser.add_argument("-r", "--restart_after", type=int,
            dest="generation", default=0,
            help="restart if do not improve for N generation")
    args = parser.parse_args()

    PUZZLE = sudoku.parse(args.file)
    budget = args.budget
    sol = ga(args.pop_size, args.ratio, args.generation)
    print("")
    print(sol)
    if sol.fitness != 0:
        print("fail to solve (best: %d)" % sol.fitness)
