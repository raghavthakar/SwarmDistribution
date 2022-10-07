import numpy as np
import taskgraph

# Q matrix stores the traits of each specie
# each row has the traits for a specie
Q = np.array([[1, 0, 1, 0],
              [0, 1, 1, 1],
              [1, 1, 1, 1]])

# S vector stores the number of agents of each specie in the system
S = np.array([12, 11, 12])

# T matrix stores the trait requirements of each task
# each row has the required traits for a task
T = np.array([[5, 2, 6, 4],
              [3, 1, 4, 2],
              [3, 2, 3, 1],
              [0, 0, 0, 0]])

tg = taskgraph.TaskGraph(T, S)

# manually initialise the t=0 distribution of agents
# among the tasks
tg.initialDistribution(np.array([[0.0, 0.0, 0.0],
                                 [0.0, 0.0, 0.0],
                                 [0.0, 0.0, 0.0],
                                 [1.0, 1.0, 1.0]]))

# manually compute the distribution of traits across tasks
tg.computeTraitDistribution(Q)

tg.display()