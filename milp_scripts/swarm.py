'''class to represent the whole swarm made up of several species'''
import numpy
import random
import taskgraph

class Swarm():
    # S
    # Q
    # num_species
    # P
    # task_ids
    def __init__(self, Q, S, task_ids):
        # Q is the matrix storing traits of each specie
        self.Q = Q

        # S contains number of agents in each specie
        self.S = S

        self.num_species = len(S)

        self.task_ids = task_ids

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
                    agent_wise_tasks += [task_num]*specie[task_num]
            self.P.append(agent_wise_tasks)
    
    # compute the transitions from current task to next task based on
    # K matrix and then assign the post-transition states to P
    def computeAndAssignTransitions(self, K):
        for specie in range(len(self.P)): #loop through each specie
            for agent in range(len(self.P[specie])): #loop through agents of each specie
                # find which task has been alloted to the agent
                alloted_task = self.P[specie][agent]
                # choose a transition out from current task based on K
                task_transition_vector = K[specie][alloted_task]
                transitioned_task = random.choices(self.task_ids, weights=task_transition_vector)
                self.P[specie][agent] = transitioned_task[0]
    
    # return the P matrix
    def getP(self):
        return self.P
    
    def display(self):
        print("Alloted Target matrix P: \n", self.P)