# -*- coding: utf-8 -*-

import random, sys, copy

class Problem(object):
    def __init__(self, numstr):
        self.board = []
        self.holes = []
        self.candidates = dict()
        for char in numstr:
            assert char.isdigit()
            num = int(char)
            assert 0 <= num and num <= 9
            self.board.append(int(char))
        for idx,val in enumerate(self.board):
            if val == 0:
                self.holes.append(idx)
                # candidates
                candidates = set(range(1,10)) \
                        - set([self.board[i] for i in neighbor(idx)])
                self.candidates[idx] = list(candidates)
        
        while True:
            if self.fill_naked_singles():  continue
            if self.fill_hidden_singles(): continue
            break

        assert len(self.board)==81

    def update_candidates(self):
        for idx in self.holes:
            candidates = set(range(1,10)) \
                    - set([self.board[i] for i in neighbor(idx)])
            self.candidates[idx] = list(candidates)

    def fill_naked_singles(self):
        changed = False
        while True:
            same = True
            for idx in list(self.candidates.keys()):
                if len(self.candidates[idx]) == 1:
                    same = False
                    changed = True
                    self.board[idx] = self.candidates[idx][0]
                    self.holes.remove(idx)
                    self.candidates.pop(idx)
            if same: break
            self.update_candidates()
        return changed

    def fill_hidden_singles(self):
        changed = False
        for unit in rows + columns + boxes:
            candidates = []
            for idx in unit:
                if idx in self.holes:
                    candidates += self.candidates[idx]
            for i in range(1,10):
                if candidates.count(i) == 1:
                    changed = True
                    for idx in unit:
                        if idx in self.holes \
                                and i in self.candidates[idx]:
                                    self.board[idx] = i
                                    self.holes.remove(idx)
                                    self.candidates.pop(idx)
                    self.update_candidates()
        return changed


    def __repr__(self):
        string = ''
        for i in range(9):
            for j in range(9):
                num = self.board[9 * i + j]
                if num:
                    string += str(num)
                else:
                    string += '.'
                string += ' '
                if j % 3 == 2 and j != 8:
                    string += '|'
            string += '\n'
            if i % 3 == 2 and i != 8:
                string += '------+------+------\n'
        return string[:-1]

class Solution(object):
    def __init__(self, problem):
        self.problem = problem
        self.holes = [0] * len(self.problem.holes)
        self.board = copy.copy(self.problem.board)
        self.fitness = sys.maxsize

    def __apply__(self):
        for i, idx in enumerate(self.problem.holes):
            self.board[idx] = self.holes[i]

    def __repr__(self):
        self.__apply__()
        string = ''
        for i in range(9):
            for j in range(9):
                num = self.board[9 * i + j]
                if num:
                    string += str(num)
                else:
                    string += '.'
                string += ' '
                if j % 3 == 2 and j != 8:
                    string += '|'
            string += '\n'
            if i % 3 == 2 and i != 8:
                string += '------+------+------\n'
        return string[:-1]

    def evaluate(self):
        self.__apply__()
        self.fitness = 0
        for idxl in boxes + rows + columns:
            self.fitness += 9 - len(set([self.board[i] for i in idxl]))
        return self.fitness

    def copy(self):
        dup = Solution(self.problem)
        dup.holes = copy.copy(self.holes)
        return dup

rows = [[i * 9 + j for j in range(9)] for i in range(9)]
columns = [[i + j * 9 for j in range(9)] for i in range(9)]
box = [0,1,2,9,10,11,18,19,20]
coners = [0,3,6,27,30,33,54,57,60]
boxes = [[i+j for j in box] for i in coners]
del box, coners

def related_units(idx):
    row = idx // 9
    col = idx % 9
    box = (idx // 27) * 3 + (idx // 3) % 3
    return [rows[row], columns[col], boxes[box]]

def neighbor(idx):
    return list(set(sum(related_units(idx),[])))

def parse(fname):
    file = open(fname)
    numstr = ''
    for line in file:
        for char in line:
            if char.isdigit():
                numstr += char
            elif char == '.':
                numstr += '0'
    sudoku = Problem(numstr)
    return sudoku

def solve(problem, n=1):
    sol = Solution(problem)
    min_fitness = sys.maxsize
    for _ in range(n):
        for i, idx in enumerate(problem.holes):
            sol.holes[i] = random.choice(problem.candidates[idx])
        sol.evaluate()
        if sol.fitness < min_fitness:
            min_fitness = sol.fitness
            solution = sol.copy()
    solution.evaluate()
    return solution

def main():
    problem = parse(sys.argv[1])
    print(problem)
    print("")
    sol = solve(problem, 10)
    print(sol)
    print(sol.fitness)

if __name__ == "__main__":
    main()
