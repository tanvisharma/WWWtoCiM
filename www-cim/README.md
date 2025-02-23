Contents:
0. Code for deriving the GEMM shapes from real workloads and input gemm shapes.
    Location: [my-inputs/raw-processing/](my-inputs/raw-processing/)
    Location: [my-inputs/workloads/*.txt](my-inputs/workloads/)
1. Technology files for specifications of different CiM Primitives.
    Location: [my-inputs/cim-library-accelergy](my-inputs/cim-library-accelergy/) for cim energy specifications for accelergy
    Location: [my-inputs/primitives](my-inputs/primitives/) for cim area, latency and parallelism specifications
2. Dataflow/mapping Algorithm.
    Location: [constraints/](constraints/)
3. Setup for evaluating the CiM Primitives and tensor-core-like design for GEMMs.
    Location: [run.py](run.py)
4. Scripts for reading the results, extracting evaluation metrics and plotting figures.
    Location: [post-process](post-process/)



