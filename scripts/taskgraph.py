'''This file handles the graph of tasks, 
allocates task requirements to each task
and has methods to compute the distribution etc'''
import numpy as np
import swarm

class TaskGraph():
    # num_tasks
    # num_traits
    # K
    # Xt
    # Yt
    # task_ids

    def __init__(self, T, S, K, task_ids):
        self.num_tasks, self.num_traits = T.shape
        
        # declare the transition probability matrix
        self.K = K
        
        self.task_ids = task_ids
        
        # declare the matrix that stores the distribution of
        # agents across the tasks. Initialised to no distribution
        # each row is a task and each column is a specie
        self.Xt = np.zeros((self.num_tasks, S.size))
        # another matrix of the same size to maintain the average distribution of agents
        self.Xt_bar = np.zeros((self.num_tasks, S.size))

        # declare the matric that stores the distribution of
        # traits across the tasks.
        self.Yt = np.zeros((self.num_tasks, self.num_traits))
        # matrix to store the average train distribution
        self.Yt_bar = np.zeros((self.num_tasks, self.num_traits))
    
    # takes the starting distribution and assigns it to Xt
    def initialDistribution(self, D):
        self.Xt = D
    
    # uses the agent-task mapping to update distribution of agents across tasks (Xt)
    def updateAgentDistribution(self, P):
        print("Updating agent distribution")
        for task in self.task_ids:
            for specie in range(len(P)):
                self.Xt[task][specie] = 0 #set the num of agents at task to zero
                agents_at_task = 0
                for allocated_task in P[specie]:
                    if allocated_task == task:
                        agents_at_task+=1
                
                self.Xt[task][specie] = agents_at_task
    
    # compute the distribution of traits along different tasks
    def computeTraitDistribution(self, Q):
        self.Yt = np.matmul(self.Xt, Q)
    
    # update the cumulative distribution of traits and agents (sum of each iteration)
    def updateCumulativeDistributions(self):
        self.Xt_bar = np.add(self.Xt_bar, self.Xt)
        self.Yt_bar = np.add(self.Yt_bar, self.Yt)
    
    # return the agents distribution matrix
    def getAgentDistribution(self):
        return self.Xt
    
    # return the traits distribution matrix
    def getTraitDistribution(self):
        return self.Yt
    
    # return the cumulateive agent distribution
    def getCumulativeAgentDistribution(self):
        return self.Xt_bar

    # return the cumulative trait distribution
    def getCumulativeTraitDistribution(self):
        return self.Yt_bar
    
    def display(self):
        print("Number of tasks: ", self.num_tasks)
        print("Number of traits: ", self.num_traits)
        print("Transition matrix: \n", self.K)
        print("Agent Distribution matrix: \n", self.Xt)
        print("Trait Distribution matrix: \n", self.Yt)
        print("Agent Cumulative Distribution matrix: \n", self.Xt_bar)
        print("Trait Cumulative Distribution matrix: \n", self.Yt_bar)