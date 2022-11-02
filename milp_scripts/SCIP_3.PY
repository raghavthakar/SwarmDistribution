from ortools.linear_solver import pywraplp
import math # may be useful for infinity
import sys
sys.path.append('helpers')
from points_generator import InputHandler, MatrixGenerator
from route_visualiser import Visualiser

# Workspace constants
R=5000 # (R is the maximum road distance between two depots)
U=150 # U is the maximum fuel capacity of the drone

'''
# instatiate the input handler
input_handler=InputHandler('shared/Boundary.csv', 'shared/Depots.csv', 'shared/Information.csv')

# get targets and depots list by calling the method
targets=input_handler.getTargets()
depots=input_handler.getDepots()
'''
# generatae work area for local tests
# sidelen is the number of targets along an edge
def generateLocalWorkArea(side_len, start_num, step):
    end_num = 5+step*(side_len-1)
    targets = []
    
    counter1 = 0
    while counter1 < side_len:
        counter2 = 0
        while counter2 < side_len:
            targets.append([counter1*step+5, counter2*step+5])
            counter2+=1
        counter1+=1

    depots = [[0, 0],                    [0, (5+step*(side_len))/2],                   [5+step*(side_len), 0],
            [(5+step*(side_len))/2, 0],                                              [5+step*(side_len), (5+step*(side_len))/2],
            [0, 5+step*(side_len)],    [(5+step*(side_len))/2, 5+step*(side_len)],   [5+step*(side_len), 5+step*(side_len)]]
    
    return targets, depots

side_len = int(sys.argv[1])
targets, depots = generateLocalWorkArea(side_len, 5, 5)
NUM_TARGETS=len(targets)
NUM_DEPOTS=len(depots)

print("Targets: ", targets)
print("Depots: ", depots)

# Generates an adjacency matrix from the list of targets and depots
matrix_generator=MatrixGenerator()

# Generate an adjacency matrix from the list of targets and depots
# targets first, depots second.
G=matrix_generator.generateMatrix([*targets, *depots])

# pretty print the generated matrix
for i in G:
    print(i)

# Check the validity of the depots. Every targets should have at least one depot less than U/2 units far
for i in range(NUM_TARGETS):
    valid=False
    for j in range(NUM_TARGETS, NUM_TARGETS+NUM_DEPOTS):
        if G[i][j] <= U/2:
            valid=True
            break
    if not valid:
        print("Invalid depots. Target", i, " has no depot within U/2 = ", U/2)
        exit()

# Making the refueling sites matrix (with road network)
# Let it be the same as the aerial distance between the depots for now
# which means its the bottom right matrix
# Again, only for now
Gr=[]
for i in range(NUM_TARGETS, NUM_TARGETS+NUM_DEPOTS):
    row=[]
    for j in range(NUM_TARGETS, NUM_TARGETS+NUM_DEPOTS):
        row.append(G[i][j])
    Gr.append(row)

print("Gr: ", Gr)

# Declaring the solution matrix X that will contain the path
X=[]

# Array will store the u variable for each target
u=[]

# matrix will store whether a depot is the last visited depot for each target
# Targets downwards, depots rightwards
Y=[]

# N set holds all the neghbour depots of a depot s that are less than or equal to R units away
N=[]
for i in range(NUM_TARGETS, NUM_TARGETS+NUM_DEPOTS):
    temp=[]
    for j in range(NUM_TARGETS, NUM_TARGETS+NUM_DEPOTS):
        if i != j and Gr[i-NUM_TARGETS][j-NUM_TARGETS] <= R:
            temp.append(j) # append the index of this valid neighbour of depot
    N.append(temp)

print("N: ", N)

# M is the constant used in fuel constraints. M = U + Max(fij)
M=0
for i in range(NUM_TARGETS):
    for j in range(NUM_TARGETS):
        if G[i][j]>M: M=G[i][j]
M+=U
print("M: ", M)

# _____________________LINEAR OPTIMISER_________________________________________________________________________________________
def FCURPHO():
    """Fuel Constrained UAV Routing Problem With Human Operator"""
    # Instantiate a SCIP solver, naming it FCURPHO.

    solver=pywraplp.Solver.CreateSolver('SCIP')
    
    # [START VARIABLE]---------------------------------------------------------
    # Create X matrix
    for i in range(len(G)):
        temp=[]
        for j in range(len(G[i])):
            temp.append(solver.IntVar(0, 1, str(i)+','+str(j)))
        X.append(temp)
    
    # Create u variable for each target
    for i in range(NUM_TARGETS):
        u.append(solver.NumVar(0, U, ('u_'+str(i))))
    
    # Create the Y variable for every target-depot combination
    for i in range(NUM_TARGETS):
        temp=[]
        for j in range(NUM_DEPOTS):
            temp.append(solver.IntVar(0, 1, 'Y_'+str(i)+','+str(j)))
        Y.append(temp)

    # [END VARIABLE]
    print('Number of variables =', solver.NumVariables())

    # [START CONSTRAINTS]-------------------------------------------------------------------------------------------------------
    
    # ________CONSTRAINT 1________
    # add the in degree and out degree constraints that for all vertices they should be equal
    # constraint implies that Summation P[i][j] for all j = Summation P[j][i] for all j ( i is fixed) should be true for all i
    constraints1=[]
    for i in range(NUM_TARGETS+NUM_DEPOTS):
        constraints1.append(solver.Constraint(0, 0))
        for j in range(NUM_TARGETS+NUM_DEPOTS):
                constraints1[-1].SetCoefficient(X[j][i], 1)
                constraints1[-1].SetCoefficient(X[i][j], -1)

    # ________CONSTRAINT 2________
    # All the targets must be travelled to at exactly once
    # It means the out degree and in degree should be =1
    constraints2=[]
    for t in range(NUM_TARGETS):
        constraints2.append(solver.Constraint(1, 1)) # out degree should be 1
        for i in range(NUM_TARGETS+NUM_DEPOTS):
            if i != t:
                constraints2[-1].SetCoefficient(X[i][t], 1) # out degree added in loop to above constraint for comparison
    
    # ________CONSTRAINT 3________
    # fuel constraint 1: ut - uj + M*xjt<= M - fjt
    constraints3=[]
    for j in range(NUM_TARGETS):
        for t in range(NUM_TARGETS):
            constraints3.append(solver.Constraint(-solver.infinity(), M-G[j][t]))
            constraints3[-1].SetCoefficient(u[t], 1)
            constraints3[-1].SetCoefficient(u[j], -1)
            constraints3[-1].SetCoefficient(X[j][t], M)
    
    # ________CONSTRAINT 4________
    # fuel constraint 2: ut - uj - M*xjt>= -M - fjt
    constraints4=[]
    for j in range(NUM_TARGETS):
        for t in range(NUM_TARGETS):
            constraints4.append(solver.Constraint(-M-G[j][t], solver.infinity()))
            constraints4[-1].SetCoefficient(u[t], 1)
            constraints4[-1].SetCoefficient(u[j], -1)
            constraints4[-1].SetCoefficient(X[j][t], -M)
    
    # ________CONSTRAINT 5_______
    # fuel constraint 3: ut + M*xkt <= M − fkt + U, ∀t ∈ T, ∀k ∈ S,
    # going from depot to targets
    constraints5=[]
    for k in range(NUM_TARGETS, NUM_TARGETS+NUM_DEPOTS):
        for t in range(NUM_TARGETS):
            constraints5.append(solver.Constraint(-solver.infinity(), M-G[k][t]+U))
            constraints5[-1].SetCoefficient(u[t], 1)
            constraints5[-1].SetCoefficient(X[k][t], M)
    
    # ________CONSTRAINT 6_______
    # fuel constraint 4: ut - M*xkt >= -M − fkt + U, ∀t ∈ T, ∀k ∈ S,
    # going from depot to targets
    constraints6=[]
    for k in range(NUM_TARGETS, NUM_TARGETS+NUM_DEPOTS):
        for t in range(NUM_TARGETS):
            constraints6.append(solver.Constraint(-M-G[k][t]+U, solver.infinity()))
            constraints6[-1].SetCoefficient(u[t], 1)
            constraints6[-1].SetCoefficient(X[k][t], -M)
    
    # ________CONSTRAINT 7_______
    # fuel constraint 5: −ut + M*xtk <= + M - ftk, ∀t ∈ T, ∀k ∈ S
    # going from targets to depots
    constraints7=[]
    for k in range(NUM_TARGETS, NUM_TARGETS+NUM_DEPOTS):
        for t in range(NUM_TARGETS):
            constraints7.append(solver.Constraint(-solver.infinity(), M-G[t][k]))
            constraints7[-1].SetCoefficient(u[t], -1)
            constraints7[-1].SetCoefficient(X[t][k], M)
    
    # ________CONSTRAINT 8_______
    # fuel constraint 6: fij * xij ≤ U ∀i , j ∈ S
    constraints8=[]
    for i in range(NUM_TARGETS, NUM_TARGETS+NUM_DEPOTS):
        for j in range(NUM_TARGETS, NUM_TARGETS+NUM_DEPOTS):
            constraints8.append(solver.Constraint(-solver.infinity(), U))
            constraints8[-1].SetCoefficient(X[i][j], G[i][j])
    
    # ________CONSTRAINT 9_______
    # fuel constraint 7: Summation(fij*xij) for all i, j in V <= U*Summation(xki) for all k in S and i in V
    constraints9=[]
    constraints9.append(solver.Constraint(-solver.infinity(), 0))
    for i in range(NUM_TARGETS+NUM_DEPOTS):
        for j in range(NUM_TARGETS+NUM_DEPOTS):
            constraints9[-1].SetCoefficient(X[i][j], G[i][j])
    for k in range(NUM_TARGETS, NUM_TARGETS+NUM_DEPOTS):
        for i in range(NUM_TARGETS+NUM_DEPOTS):
            constraints9[-1].SetCoefficient(X[k][i], -U)
    
    # ________CONSTRAINT 10_______
    # refuel site constraint 1: yts − xst ≥ 0, ∀t ∈ T, s ∈ S
    constraints10=[]
    for t in range(NUM_TARGETS):
        for s in range(NUM_TARGETS, NUM_TARGETS+NUM_DEPOTS):
            constraints10.append(solver.Constraint(0, solver.infinity()))
            constraints10[-1].SetCoefficient(Y[t][s-NUM_TARGETS], 1)
            constraints10[-1].SetCoefficient(X[s][t], -1)
    
    # ________CONSTRAINT 11_______
    # refuel site constraint 2: yt2s − yt1s + xt1t2 <= (1) ∀s ∈ S, ∀t 1, t2 ∈ T
    constraints11=[]
    for s in range(NUM_TARGETS, NUM_TARGETS+NUM_DEPOTS):
        for t1 in range(NUM_TARGETS):
            for t2 in range(NUM_TARGETS):
                constraints11.append(solver.Constraint(-solver.infinity(), 1))
                constraints11[-1].SetCoefficient(Y[t2][s-NUM_TARGETS], 1)
                constraints11[-1].SetCoefficient(Y[t1][s-NUM_TARGETS], -1)
                constraints11[-1].SetCoefficient(X[t1][t2], 1)
    
    # ________CONSTRAINT 12______
    # refuel site constraint 3: yt2s − yt1s − xt1t2 >= (-1) ∀s ∈ S, ∀t 1, t2 ∈ T
    constraints12=[]
    for s in range(NUM_TARGETS, NUM_TARGETS+NUM_DEPOTS):
        for t1 in range(NUM_TARGETS):
            for t2 in range(NUM_TARGETS):
                constraints12.append(solver.Constraint(-1, solver.infinity()))
                constraints12[-1].SetCoefficient(Y[t2][s-NUM_TARGETS], 1)
                constraints12[-1].SetCoefficient(Y[t1][s-NUM_TARGETS], -1)
                constraints12[-1].SetCoefficient(X[t1][t2], -1)
    
    # ________CONSTRAINT 13______
    # refuel site constraint 4: 
    constraints13=[]
    for s in range(NUM_TARGETS, NUM_TARGETS+NUM_DEPOTS):
        for t in range(NUM_TARGETS):
            constraints13.append(solver.Constraint(-solver.infinity(), 1))
            constraints13[-1].SetCoefficient(Y[t][s-NUM_TARGETS], 1)
            for k in range(NUM_TARGETS, NUM_TARGETS+NUM_DEPOTS): # iterate through all depots, add constraint for depots not in N(s)
                if k not in N[s-NUM_TARGETS]: # look through the row in N matrix corresponding to s
                    constraints13[-1].SetCoefficient(X[t][k], 1)

    # ________CONSTRAINT 14______
    # refuel site constraint 5: 
    constraints14=[]
    for s in range(NUM_TARGETS, NUM_TARGETS+NUM_DEPOTS):
            constraints14.append(solver.Constraint(0, 0))
            for k in range(NUM_TARGETS, NUM_TARGETS+NUM_DEPOTS): # iterate through all depots, add constraint for depots not in N(s)
                if k not in N[s-NUM_TARGETS]: # look through the row in N matrix corresponding to s
                    constraints14[-1].SetCoefficient(X[s][k], 1)
    
    # ________CONSTRAINT 15______
    # refuel site constraint 6: 
    constraints15=[]
    for t in range(NUM_TARGETS):
        constraints15.append(solver.Constraint(1, 1))
        for s in range(NUM_TARGETS, NUM_TARGETS+NUM_DEPOTS):
            constraints15[-1].SetCoefficient(Y[t][s-NUM_TARGETS], 1)
    
    # _______CONSTRAINT 16_______
    # Lazy constraint to avoid subtours in solution

    
    # [END CONSTRAINTS]

    # [START OBJECTIVE]-------------------------------------------------------------------------------------------------------
    # The objective function states that the cost of the entire travel should be minimum
    # I think summation of X[i][j]*G[i][j] over all i and all j should be minimum
    objective=solver.Objective()
    for i in range(len(G)):
        for j in range(len(G[i])):
            objective.SetCoefficient(X[i][j], G[i][j]) # multipling the path variable with corresponding weight
    objective.SetMinimization()
    

    # [END OBJECTIVE]

     # [START SOLVING]-------------------------------------------------------------------------------------------------------
    solver.Solve()

    # [START DISPLAYING]-------------------------------------------------------------------------------------------------------
    num_edges=0
    for i in range(len(G)):
        for j in range(len(G[i])):
            print(str(round(X[i][j].solution_value()))+" ", end="")
            num_edges+=X[i][j].solution_value()
        print()
    
    print("Cost of travel: ", solver.Objective().Value())
    print("number of edges: "+str(num_edges))
    file1 = open("myfile.txt", "a")  # append mode
    file1.write(str(solver.Objective().Value())+"\n")
    file1.close()
    # [END DISPLAYING]-------------------------------------------------------------------------------------------------------

    # [START VISUALISATION]--------------------------------------------------------------------------------------------------
    # Loop through the entire matrix and generate a new matrix with only the solution values
    # store it in solution_matrix
    solution_matrix=[]
    for i in X:
        row=[]
        for j in i:
            row.append(round(j.solution_value()))
        solution_matrix.append(row)
    solution_matrices=[]
    solution_matrices.insert(0, solution_matrix)

    print("______________")
    print(solution_matrix)
    
    # route visualiser object will be used to visualise the generated route
    route_visualiser=Visualiser()
    route_visualiser.visualise(solution_matrices, targets, depots)
    # [END VISUALISATION]--------------------------------------------------------------------------------------------------

    # [START MISSION FILE GENERATION]--------------------------------------------------------------------------------------
    # [END MISSION FILE GENERATION]----------------------------------------------------------------------------------------

FCURPHO()