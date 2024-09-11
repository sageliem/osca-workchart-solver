from pulp import *
import csv

print(listSolvers(onlyAvailable=True))

# Constants
hours = 1
days = 7
DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', '']

avail = [] # Availability stored as list of ['Name', [morning avail], [afternoon avail], [evening avail]]
with open('input.csv', mode = 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        av_M = [0] * 8
        av_A = [0] * 8
        av_E = [0] * 8
        # print(row)
        for avail_day in row['morning'].split(', '):
            av_M[DAY_NAMES.index(avail_day)] = 1
        for avail_day in row['afternoon'].split(', '):
            av_A[DAY_NAMES.index(avail_day)] = 1
        for avail_day in row['evening'].split(', '):
            av_E[DAY_NAMES.index(avail_day)] = 1

        for avail_day in row['best morning'].split(', '):
            av_M[DAY_NAMES.index(avail_day)] = 2
        for avail_day in row['best afternoon'].split(', '):
            av_A[DAY_NAMES.index(avail_day)] = 2
        for avail_day in row['best evening'].split(', '):
            av_E[DAY_NAMES.index(avail_day)] = 2

        avail.append([row['\ufeffname'], av_M, av_A, av_E]) 

members = len(avail)

#Define problem
problem = LpProblem('shift', LpMaximize)
M = LpVariable.dicts('Morning', (range(days), range(members)), 0, 1, 'Binary')
A = LpVariable.dicts('Afternoon', (range(days), range(members)), 0, 1, 'Binary')
E = LpVariable.dicts('Evening', (range(days), range(members)), 0, 1, 'Binary')


# Objective Function: maximize number of preferred shifts 
obj = 0
for d in range(days):
    for m in range(members):
        obj += (avail[m][1][d] * M[d][m]) + (avail[m][2][d] * A[d][m]) + (avail[m][3][d] * E[d][m])
problem += obj
# print(problem.objective)

# Constraints
# Max 1 hour
for m in range(members):
    c = None
    for d in range(7):
        c += M[d][m] + A[d][m] + E[d][m]
    problem += (c==hours)

# Minimum/maximum resources
min_per_shift = 1
max_per_shift = 2
for d in range(7):
    mor = None
    aft = None
    eve = None

    for m in range(members):
        mor += M[d][m] 
        aft += A[d][m]
        eve += E[d][m]
    problem += mor >= min_per_shift
    problem += aft >= min_per_shift
    problem += eve >= min_per_shift

    problem += mor <= max_per_shift
    problem += aft <= max_per_shift
    problem += eve <= max_per_shift


problem.writeLP("WorkchartModel.lp")
problem.solve(PULP_CBC_CMD())
print("Status:", LpStatus[problem.status])

if LpStatus[problem.status] == 'Optimal':
    for d in range(7):
        shift_m = ''
        shift_a = ''
        shift_e = ''
        for m in range(members):
            if value(M[d][m]) == 1.0:
                shift_m = avail[m][0]
            if value(A[d][m]) == 1.0:
                shift_a = avail[m][0]
            if value(E[d][m]) == 1.0:
                shift_e = avail[m][0]
        print(DAY_NAMES[d], "Morning:", shift_m)
        print(DAY_NAMES[d], "Afternoon:", shift_a)
        print(DAY_NAMES[d], "Evening:", shift_e)
    #for var in problem.variables():
    #    print(var, "=", value(var))

#print("morning: ", M)
