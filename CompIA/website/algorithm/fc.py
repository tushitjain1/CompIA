from random import shuffle

# Solution for the algorithm
global solution
solution = []


# There are no more values in the domain for this variable
def DWO(variable):
    for x in variable.domain[1]:
        if x == 0:
            return False
    return True


def RESTORE(listOfVariables, level):
    for x in listOfVariables:
        for i in x.domain[1]:
            if i == level:
                i = 0
    return listOfVariables


def CHECK_FORWARD(listOfVariables, level, variable, value, constraints):
    for x in listOfVariables:
        if (variable, x) in constraints:
            for y in x.domain[0]:
                if x.domain[1][x.domain[0].index(y)] == 0:
                    if y == value:
                        x.domain[1][x.domain[0].index(y)] = level
            if DWO(x):
                return False
    return True


def Search_FC(listOfVariables, level, constraints):
    global solution
    shuffle(listOfVariables)
    selectedVariable = listOfVariables[0]
    for i in selectedVariable.domain[0]:
        if selectedVariable.domain[1][selectedVariable.domain[0].index(i)] == 0:
            temp = (selectedVariable, i)
            solution.append(temp)
            if selectedVariable == listOfVariables[-1]:
                return True
            else:
                copy = []
                for x in listOfVariables:
                    if x == selectedVariable:
                        continue
                    else:
                        copy.append(x)
                if CHECK_FORWARD(copy, level, selectedVariable, i, constraints) and Search_FC(copy, level + 1,
                                                                                              constraints):
                    return True
                else:
                    solution.remove(temp)
                    listOfVariables = RESTORE(copy, level)
    return False  # there is no solution
