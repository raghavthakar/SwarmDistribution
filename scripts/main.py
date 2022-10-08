import numpy as np
import taskgraph
import swarm

# Q matrix stores the traits of each specie
# each row has the traits for a specie
Q = np.array([[1, 0, 1, 0],
              [0, 1, 1, 1],
              [1, 1, 0, 1]])

# S vector stores the number of agents of each specie in the system
S = np.array([10, 6, 12])

# assigns an ID to each task (use 0, 1, 2.. for easy indexing)
task_ids = [0, 1, 2, 3]

# intiialise a swarm
main_swarm = swarm.Swarm(Q, S, task_ids)

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

# execute one transition iteration and store new allocations
main_swarm.computeAndAssignTransitions(K)
main_swarm.display()

tg.updateAgentDistribution(main_swarm.getP())
# manually compute the distribution of traits across tasks
tg.computeTraitDistribution(Q)
tg.display()
