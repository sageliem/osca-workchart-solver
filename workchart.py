import sys
import csv
from pulp import *

if len(sys.argv) != 2:
    print("Please specify one file.")
    sys.exit()

# Constants
days = 7
DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', '']

# Set number of hours per person, min/max per shift
hours = 1
min_hours = 1
max_hours = 2

# Set column locations of scheduling data
NAME_KEY = 2
ALL_MOR_KEY = 8
ALL_AFT_KEY = 9
ALL_EVE_KEY = 10
BEST_MOR_KEY = 4
BEST_AFT_KEY = 5
BEST_EVE_KEY = 6
HAS_POS_KEY = 13

avail = [] # Availability stored as list of ['Name', [morning avail], [afternoon avail], [evening avail]]

with open(sys.argv[1], mode = 'r') as file:
    reader = csv.reader(file)
    next(reader)
    next(reader)
    for row in reader:
        if row[HAS_POS_KEY] != 'Yes':
            # Availability lists (per person, by day of week) Includes 8th empty slot to handle empty slots
            av_M = [0] * 8 
            av_A = [0] * 8
            av_E = [0] * 8

            for avail_day in row[ALL_MOR_KEY].split(', '):
                av_M[DAY_NAMES.index(avail_day)] = 1
            for avail_day in row[ALL_AFT_KEY].split(', '):
                av_A[DAY_NAMES.index(avail_day)] = 1
            for avail_day in row[ALL_EVE_KEY].split(', '):
                av_E[DAY_NAMES.index(avail_day)] = 1
            
            best_avail_weight = 1.01
            for avail_day in row[BEST_MOR_KEY].split(', '):
                av_M[DAY_NAMES.index(avail_day)] = best_avail_weight
            for avail_day in row[BEST_AFT_KEY].split(', '):
                av_A[DAY_NAMES.index(avail_day)] = best_avail_weight
            for avail_day in row[BEST_EVE_KEY].split(', '):
                av_E[DAY_NAMES.index(avail_day)] = best_avail_weight

            avail.append([row[2], av_M, av_A, av_E]) 

members = len(avail) # total membership (excluding elected positions)

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
    # Counters
    mor = 0
    aft = 0
    eve = 0
    # count people assigned to each shift
    for m in range(members):
        mor += M[d][m] 
        aft += A[d][m]
        eve += E[d][m]
    problem += mor >= min_per_shift
    problem += aft >= min_per_shift

    problem += mor <= max_per_shift
    problem += aft <= max_per_shift
    if d == 4 or d == 5: # Weekend evening
        problem += eve == 0
    else:
        problem += (eve >= min_per_shift)
        problem += (eve <= max_per_shift)

# Solve problem using cbc solver
problem.writeLP("WorkchartModel.lp")
problem.solve(PULP_CBC_CMD())
print("Status:", LpStatus[problem.status])

# Print results
if LpStatus[problem.status] == 'Optimal':
    for d in range(7):
        shift_m = ''
        shift_a = ''
        shift_e = ''
        for m in range(members):
            if value(M[d][m]) == 1.0:
                shift_m += avail[m][0]
            if value(A[d][m]) == 1.0:
                shift_a += avail[m][0]
            if value(E[d][m]) == 1.0:
                shift_e += avail[m][0]
        print(DAY_NAMES[d], "Morning:", shift_m)
        print(DAY_NAMES[d], "Afternoon:", shift_a)
        print(DAY_NAMES[d], "Evening:", shift_e)
