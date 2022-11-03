from ortools.linear_solver import pywraplp
import numpy as np
import taskgraph
import swarm

def simulation(Q, S, task_ids, T, D, K):
    # intiialise a swarm
    main_swarm = swarm.Swarm(Q, S, task_ids)

    tg = taskgraph.TaskGraph(T, S, K, task_ids)

    # manually initialise the t=0 distribution of agents
    # among the tasks. Columns are species, rows are tasks,
    # Important to note that distributions traxk the number of agents
    # at a site and not their proportion distribution
    tg.initialDistribution(D)

    # initialise the swarm distribution according to the initial distribution
    main_swarm.initialAssignment(D)

    # manually compute the distribution of traits across tasks
    tg.computeTraitDistribution(Q)

    main_swarm.display()
    tg.display()

    num_iters = 250
    for i in range(num_iters):
        # execute one transition iteration and store new allocations
        main_swarm.computeAndAssignTransitions(K)
        main_swarm.display()

        tg.updateAgentDistribution(main_swarm.getP())
        # manually compute the distribution of traits across tasks
        tg.computeTraitDistribution(Q)
        # update the cumulative agent and trait distribution across the tasks
        tg.updateCumulativeDistributions()
        tg.display()

    print("Average agent distribution: \n", np.divide(tg.getCumulativeAgentDistribution(), num_iters))
    print("Average trait distribution: \n", np.divide(tg.getCumulativeTraitDistribution(), num_iters))

# all the linear optimsiation stuff to find feasible linear combinations
def LinearOptimiser(Q, S, task_ids, T, D, K):

    # instantiate a linear solver
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # [START VARIABLES]-----------
    # 1. Create X matrix that stores tasks vs agents of species
    X=[]
    for i in range(len(task_ids)): #as many rows as number of tasks
        temp_row = []
        for j in range(len(Q)): #as many columns as number of species
            temp_row.append(solver.IntVar(0, solver.infinity(), str(i)+'_'+str(j)))
        X.append(temp_row)
    
    print("X:", X)
    
    # 2. Create the T_bar matrix that stores the product of X and Q to give task vs trait
    T_bar=[]
    for i in range(len(task_ids)): #as manu rows as number of tasks
        temp_row = []
        for j in range(len(Q[0])): #as many columns as number of traits
            temp_row.append(solver.IntVar(0, solver.infinity(), str(i)+'_'+str(j)))
        T_bar.append(temp_row)
    
    print("T_bar: ", T_bar)

    # [END VARIABLES]-----------
    print('Number of variables =', solver.NumVariables())

    # [START CONSTRAINTS]-----------
    # 1. tij = summation(k=1->num(species) Xik.Qkj
    # for i 0->num_tasks-1, j 0->num_traits-1
    constraints1=[]
    for i in range(len(task_ids)): #number of tasks
        for j in range(len(Q[0])): #number of traits
            constraints1.append(solver.Constraint(0, 0)) #RHS = 0
            constraints1[-1].SetCoefficient(T_bar[i][j], -1) #subtract t'[i][j] from summation term
            # to compute the row and column computation in matrix product
            for k in range(len(Q)): #number of species
                constraints1[-1].SetCoefficient(X[i][k], int(Q[k][j]))
    
    # 2. summmation(j=1->num_tasks) Xij <= S[i]
    # for i 1->num_species
    constraints2=[]
    for i in range(len(Q)): #number of species
        constraints2.append(solver.Constraint(float(S[i]), float(S[i])))
        # compute and add the column sum
        for j in range(len(task_ids)): #number of tasks
            constraints2[-1].SetCoefficient(X[j][i], 1)

    # 3. t_bar[i][j] >= t[i][j]
    constraints3=[]
    for i in range(len(task_ids)):
        for j in range(len(Q[0])):
            constraints3.append(solver.Constraint(float(T[i][j]), solver.infinity()))
            constraints3[-1].SetCoefficient(T_bar[i][j], 1)
    # [END CONSTRAINTS]-----------

    solver.Solve()
    agent_distribution = []
    for i in range(len(X)):
        temp_row = []
        for j in range(len(X[0])):
            temp_row.append(int(X[i][j].solution_value()))
        agent_distribution.append(temp_row)
    
    return agent_distribution

# Find the TPM from knowledge of Pi
def TPMOptimisation(X_dens, Q, S, task_ids, T, D, K):

    # X_dens is the steady state probabilities
    P = []
    for i in range(len(Q)): #through the species
        temp_matrix = []
        for j in range(len(task_ids)):
            temp_matrix.append(X_dens[i])
        P.append(temp_matrix)
    
    for i in range(len(P)):
        for j in range(len(P[0])):
            for k in range(len(P[0][0])):
                print(P[i][j][k], end=" ")
            print()
        print()
    
    return P

# Q matrix stores the traits of each specie
# each row has the traits for a specie
Q = np.array([[1, 0, 1, 0],
              [1, 1, 1, 1],
              [1, 1, 0, 1]])

# S vector stores the number of agents of each specie in the system
S = np.array([5, 8, 7])

# assigns an ID to each task (use 0, 1, 2.. for easy indexing)
task_ids = [0, 1, 2, 3]

# T matrix stores the trait requirements of each task
# each row has the required traits for a task
T = np.array([[5, 2, 6, 4],
              [3, 1, 4, 2],
              [3, 2, 3, 1],
              [0, 0, 0, 0]])

# D is the initial distribution of agents across tasks
D = np.array([[0, 0, 0],
              [0, 0, 0],
              [0, 0, 0],
              S])

# K matrix stores the transition probabilities between tasks
# it is like a TPM
# for speicies 1, 2, 3 we have a 3d matrix:
K = np.array([[[0, 0.33, 0.33, 0.33], [0.33, 0, 0.33, 0.33], [0.33, 0.33, 0, 0.33], [0.33, 0.33, 0.33, 0]],
              [[0, 0.33, 0.33, 0.33], [0.33, 0, 0.33, 0.33], [0.33, 0.33, 0, 0.33], [0.33, 0.33, 0.33, 0]],
              [[0, 0.33, 0.33, 0.33], [0.33, 0, 0.33, 0.33], [0.33, 0.33, 0, 0.33], [0.33, 0.33, 0.33, 0]]])

# simulation(Q, S, task_ids, T, D, K)

# X stores the distribution of agents across the tasks
X = LinearOptimiser(Q, S, task_ids, T, D, K)
print("Agent distribution: ", X)

T_bar = np.matmul(np.array(X), np.array(Q))
print("Trait distribution: ")
print(T_bar)

# X_dens stores the fraction of a specie at a task (specie vs task)
X_dens = X.copy()
for i in range(len(X)):
    for j in range(len(X[0])):
        X_dens[i][j] = X_dens[i][j]/S[j]
X_dens = np.matrix.transpose(np.array(X_dens))
print("Agent density: ")
print(X_dens)

P = TPMOptimisation(X_dens, Q, S, task_ids, T, D, K)

simulation(Q, S, task_ids, T, D, P)















# # [START VARIABLES]-----------
#     # 1. Create a P_bar[i] matrix that is product of I-P[i] and X_dens[i]
#     P_bar = []
#     for i in range(len(Q)): #through the species
#         temp_matrix = []
#         for j in range(len(task_ids)):
#             temp_row = []
#             for k in range(len(task_ids)):
#                 temp_row.append((solver.NumVar(0, 1, "Pbar_"+str(i)+'_'+str(j)+'_'+str(k))))
#             temp_matrix.append(temp_row)
#         P_bar.append(temp_matrix)
    
#     print("P_bar: ", P_bar)

#     # 2. Create a P[i] matrix
#     P = []
#     for i in range(len(Q)): #through the species
#         temp_matrix = []
#         for j in range(len(task_ids)):
#             temp_row = []
#             for k in range(len(task_ids)):
#                 temp_row.append((solver.NumVar(0, 1, 'P_'+str(i)+'_'+str(j)+'_'+str(k))))
#             temp_matrix.append(temp_row)
#         P.append(temp_matrix)
    
#     print("P: ", P)
#     # [END VARIABLES]-----------

#     # [START CONSTRAINTS]-----------
#     # 1. Pi[j] P_bar[j][k] = 0
#     constraints1=[]
#     for i in range(len(P_bar)): #through the species
#         for j in range(len(P_bar[0])):
#             constraints1.append(solver.Constraint(-solver.infinity(), solver.infinity()))
#             for k in range(len(P_bar[0][0])):
#                 constraints1[-1].SetCoefficient(P_bar[i][k][j], X_dens[i][k])

#     # 2. P'[i] = I-P[i]
#     constraints2=[]
#     for i in range(len(P_bar)):
#         for j in range(len(P_bar[0])):
#             for k in range(len(P_bar[0][0])):
#                 constraints2.append(solver.Constraint(float(I[j][k]), float(I[j][k])))
#                 constraints2[-1].SetCoefficient(P_bar[i][j][k], 1)
#                 constraints2[-1].SetCoefficient(P[i][j][k], 1)
    
#     # 3. Row sum of P = 1
#     constraints3=[]
#     for i in range(len(P)):
#         for j in range(len(P[0])): #down the column
#             constraints3.append(solver.Constraint(1, 1))
#             for k in range(len(P[0][0])):
#                 constraints3[-1].SetCoefficient(P[i][j][k], 1)
    
#     # 4. diagonal elements in the TPM must be zero (no self loop)
#     # constraints4=[]
#     # for i in range(len(P)):
#     #     for j in range(len(P[0])):
#     #         constraints4.append(solver.Constraint(0, 0))
#     #         constraints4[-1].SetCoefficient(P[i][j][j], 1)
#     # [END CONSTRAINTS]-----------

#     solver.Solve()
#     for i in range(len(P)):
#         for j in range(len(P[0])):
#             for k in range(len(P[0][0])):
#                 print(P[i][j][k].solution_value(), end=" ")
#             print()
#         print()