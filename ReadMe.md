# Distribution of a Swarm of Heterogeneous Robots Across Tasks

This project uses a stochastic approach to distribute heterogenous agents across several task sites to fulfill the requirements at each site.

**keywords**: probabilistic task allocation, swarm robots

## Problem Setting

Consider an evironment with $m$ tasks and $n$ robots. Each robot has specific traits (like qualities/abilities) that it can lend towards satisfying a task's requirements. The requirement of a task is a linear combination of all the traits that a robot can have. When a task is occupied by enough number of agents such that the total sum of the traits possessed by each agent exceed the requirements of that task, we say that that particular task has been satisfied. The possession of a trait by an agent is a binary quantity, that is, a robot either has that trait or it doesn't. A robot can have several traits.

We take the case of our robot population being partitioned into $s$ species, such that agents in each specie possess the same combination of traits. Our task then reduces to computing the distribution of agents from each specie among the $m$ tasks such that the trait requirements of each task are satisfied. This gives us the option to treat each species individually if need be.

As we would like to approach this problem for a very large number of agents, it is important to consider the costs of monitoring and maintaining agents when their number is in the order of 100s or 1000s of robots. Hence in such applications it is desirable to treat the distribution of agents across the tasks from a stochastic or probabilistic aspect that allows us to allocate agents to tasks such that any task's requirements get satisfied consistently *on average*. This also means that agents are free to switch tasks, ensuring a rotation of agents across tasks. This helps counter the effect of defective robots getting concentrated on the same task, or the effect the traits of identical robots being slightly different in practical cases.

If we treat each task as a state in a Markov Chain, our problem then becomes to **find a Transition Probability Matrix (TPM) for each specie such that the trait requirements of each task are satisfied in the steady state**.
![](ReadME_Resources/tasks_markov_chain.png)
The above figure represents 4 tasks as states in a Markov Chain. The weight of edge between 2 states signifies the probability of an agent transitioning between the states (not necessarily the same in both directions).