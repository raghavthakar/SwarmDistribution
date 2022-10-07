'''class to represent the whole swarm made up of several species'''
import numpy
import taskgraph

class Swarm():
    # S
    # Q
    # num_species
    # P
    def __init__(self, Q, S):
        # Q is the matrix storing traits of each specie
        self.Q = Q

        # S contains number of agents in each specie
        self.S = S

        self.num_species = len(S)

        # P tracks which task site each swarm agent is at
        # each row for a species specifies task site of each agent
        # P is a list of numpy arrays. Initialised to all 0's
        self.P = []
    
    # initalise the allocations of agents to targets (value of P)
    def initialAssignment(self, D):
        for specie in D.transpose():
            agent_wise_tasks = [] # this single array tracks the task allocated to each agent of a specie
            for task_num in range(len(specie)):
                if specie[task_num] > 0:
                    agent_wise_tasks.append([task_num]*specie[task_num])
            self.P += (agent_wise_tasks)
    
    def display(self):
        print("Alloted Target matrix P: \n", self.P)