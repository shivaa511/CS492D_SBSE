import sys

notknown = set('.0*?')

def parse(fname):
    file = open(fname)
    numstr = ''
    for line in file:
        for char in line:
            if char.isdigit():
                numstr += char
            elif char in notknown:
                numstr += '0'
    return numstr

rows = [[i * 9 + j for j in range(9)] for i in range(9)]
columns = [[i + j * 9 for j in range(9)] for i in range(9)]
box = [0,1,2,9,10,11,18,19,20]
coners = [0,3,6,27,30,33,54,57,60]
boxes = [[i+j for j in box] for i in coners]
del box, coners

if __name__ == "__main__":
    numstr = parse(sys.argv[1])
    score = 0
    for idxl in rows + columns + boxes:
        score += 9 - len(set([numstr[i] for i in idxl]) - set(['0']))

    print(score)
