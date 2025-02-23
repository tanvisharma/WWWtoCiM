## Mapping Constraints Auto-generation using the proposed priority-based algorithm

### Input:
GEMM shapes (M,N,K) and the architecture specs (Rp, Cp, Rh, Ch, X, Y, Smem) given in the arguments

### Output:
 constraints: {memory<X>: {factors: [M=x, N=y, K=z], permutation: [MNK]}... CiM<components>: {factors:..permutation}


### Algorithm:
```get_mapping_constraints(M, N, K, Rp, Cp, Rh, Ch, X, Y, Smem)```

 1. Given CiM Rp and Cp, map weights (N x K) to fully leverage the intra-CiMBank parallelism. Calculate the remaining factors of N and K (```max_possible_factor``` and ```update_rem```).
 2. Given the number of CiMBanks (X, Y), find the factor of N or K that can be parallelized across multiple banks (```get_bank_factors```). Assumption: X=1, all banks in the Y dimension and only 1 dimension (N or K) can be paralleized across Y dimension of banks.
 3. Given CiM Rh and Ch, map the remaining factors of N and K to maximize CiMBank utilization.
 4. Using the K and N factors mapped to the CiMBanks, calculate the maximum factor of M such that the input matrix (MxK) and output matrix (MxN) can fit in the next memory level.
 5. Iteratively increment the value of K while ensuring the capacity constraint is met (```improvise_K```), prioritizing weight reuse.
 6. Iteratively increment the value of N while ensuring the capacity constraint is met (```improvise_N```), prioritizing output partial sum reuse.
 7. Decide the loop order based on the permutation that keeps the maximum factor in the innermost loop (```get_permutation```). 
 8. Repeat the process for the next memory level. For the architecture used in our experiements, the remaining factors will reside in the main memory (DRAM).


Limitation: No weight duplication considered in the current version of mapping algorithm.