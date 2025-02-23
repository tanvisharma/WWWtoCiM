# WWW 

Welcome to the repository for "What, When, Where to Compute-in-Memory for Efficient Matrix Multiplication during Machine Learning Inference" by Tanvi Sharma, Mustafa Ali, Indranil Chakroborty and Kaushik Roy. WWW utilizes already existing infrastructure from [Timeloop/Accelergy](https://github.com/mit-emze/cimloop) to analytically evaluate different compute in memory designs when integrated in the memory hierarchy of a [tensorcore like architecture](https://github.com/Accelergy-Project/timeloopfe/tree/main/arch_spec_examples/sparse_tensor_core_like).

![image](https://github.com/user-attachments/assets/476b8367-bca3-4bb6-a94c-3ef8b1e70aab)



## Overview
WWW compares SRAM based Compute-in-Memory designs (referred as primitives in this work) by abstracting them in terms of the following template:

![image](https://github.com/user-attachments/assets/116426db-d33f-438e-8033-bc8e15579cf0)

and deciding the dataflow using our priority based algorithm for each CiM primitive, when integrated at the shared memory and register file level.

## Contents
This repository contains the setup for 
1. Timeloopfe infrastructure ([accelergy-timeloop-infrastructure/](https://timeloop.csail.mit.edu/v4/installation) and [timeloop-accelergy-execises/](https://github.com/Accelergy-Project/timeloop-accelergy-exercises))
2. Priority based algorithm (www-cim/constraints/)
3. Data used to plot graphs in the paper (www-cim/outputs)

For the paper, please visit [WWW](https://arxiv.org/abs/2312.15896).

