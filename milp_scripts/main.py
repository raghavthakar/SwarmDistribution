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

    # [START OBJECTIVE]-----------
    # keep a constant objective to not optimise anything
    # objective = solver.Objective()
    # objective.SetCoefficient(5, 1)
    # objective.SetMinimization()

    # [END OBJECTIVE]-----------

    solver.Solve()
    for i in range(len(X)):
        for j in range(len(X[0])):
            print(str(X[i][j].solution_value())+" ", end="")
        print()

# Q matrix stores the traits of each specie
# each row has the traits for a specie
Q = np.array([[1, 0, 1, 0],
              [1, 1, 1, 1],
              [1, 1, 0, 1]])

# S vector stores the number of agents of each specie in the system
S = np.array([7, 7, 7])

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
LinearOptimiser(Q, S, task_ids, T, D, K)