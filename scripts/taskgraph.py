'''This file handles the graph of tasks, 
allocates task requirements to each task
and has methods to compute the distribution etc'''
import numpy as np

class TaskGraph():
    def __init__(self, T, S):
        self.num_tasks, self.num_traits = T.shape
        
        # declare the transition probability matrix
        self.K = np.zeros((self.num_tasks, self.num_tasks))
        # initialise K with equal transition probabilities to every other task
        for i in range(self.num_tasks):
            for j in range(self.num_tasks):
                if i != j:
                    self.K[i, j] = 1/self.num_tasks
        
        # declare the matrix that stores the distribution of
        # agents across the tasks. Initialised to no distribution
        # each row is a task and each column is a specie
        self.Xt = np.zeros((self.num_tasks, S.size))

        # declare the matric that stores the distribution of
        # traits across the tasks.
        self.Yt = np.zeros((self.num_tasks, self.num_traits))
    
    # takes the starting distribution and assigns it to Xt
    def initialDistribution(self, D):
        self.Xt = D
    
    # compute the distribution of traits along different tasks
    def computeTraitDistribution(self, Q):
        self.Yt = np.matmul(self.Xt, Q)
    
    def display(self):
        print("Number of tasks: ", self.num_tasks)
        print("Number of traits: ", self.num_traits)
        print("Transition matrix: \n", self.K)
        print("Agent Distribution matrix: \n", self.Xt)
        print("Trait Distribution matrix: \n", self.Yt)