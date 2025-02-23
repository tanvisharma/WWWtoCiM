
"""
Script to compare results (gain/speedup) across workloads in terms of TOPS/W, GFLOPs and Utilization,
    1. Between baseline (arch1) and a CiM primitive.
    2. Between two CiM primitive types (arch1 and arch2) at RF/SMEM level (dir1 and dir2), with iso-area constraints.
    3. Between same CiM primitive with and without constraints.
"""

import os
import argparse
from get_stats import dump_stats
import numpy as np
import csv 

CIM_PRIMITIVES_PATH = f"{os.curdir}/../my-inputs/primitives/cim-primitives.txt"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare results from different output directories")
    parser.add_argument("--workloads", type=str, help="Name of all the workload .txt files to compare results from. Separate by space.")
    parser.add_argument("--arch1", default="tensor_core_like", help="Name of cim_type if not using baseline for comparison")
    parser.add_argument("--arch2", default="rf_compute_digital6T", help="Name of cim_type2/baseline to compare results")
    parser.add_argument("--dir1", default="outputs", help="Name of the output directory for arch1. ENSURE to change this if arch1 is a cim type.")
    parser.add_argument("--dir2", default="outputs_consv2p1_isoarea", help="Name of the output directory for arch2. ")

    args = parser.parse_args()

    stats_1 = np.array([])
    stats_2 = np.array([])

    workloads = args.workloads.split(" ")
    tops_w_avg = []
    tops_w_stddev = []
    gflops_avg = []
    gflops_stddev = []
    util_avg = []
    util_stddev = []
    for workload in workloads:
        with open(workload, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            next(reader)
            # x1 = []
            # x2 = []
            # x3 = []
            # y = []
            for row in reader:
                modelname = row[0]
                M = row[1]
                N = row[2]
                K = row[3]

                # output directory name
                output_dir_org = f"{os.curdir}/../outputs/{args.arch1}/{modelname}/{args.dir1}/{M}_{N}_{K}"
                output_dir_comp = f"{os.curdir}/../outputs/{args.arch2}/{modelname}/{args.dir2}/{M}_{N}_{K}"


                cimtype1 = ""
                if args.arch1 == "tensor_core_like":
                    cimtype1 = "tensor_core_like"
                else:
                    # divide the arch name by '_compute_'
                    cimtype1 = args.arch1.split("_compute_")[1]

                cimtype2 = args.arch2.split("_compute_")[1]


                entry_1 = dump_stats(output_dir_org, cimtype1, CIM_PRIMITIVES_PATH)
                entry_1 = np.array(entry_1).reshape(1, -1)

                entry_2 = dump_stats(output_dir_comp, cimtype2, CIM_PRIMITIVES_PATH)
                entry_2 = np.array(entry_2).reshape(1, -1)

                # append to stats_1 and stats_2
                if stats_1.size == 0:
                    stats_1 = entry_1
                    stats_2 = entry_2
                else:
                    stats_1 = np.vstack((stats_1, entry_1))
                    stats_2 = np.vstack((stats_2, entry_2))

                # M = int(M)
                # N = int(N)
                # K = int(K)
                # algo_reuse = (M*N*K)/(M*K + N*K + M*N)
                # weight_reuse = (M*N*K)/(N*K)
                # input_reuse = (M*N*K)/(M*K)
                # output_reuse = (M*N*K)/(N*M)
                # weight_size = N*K
                # input_size = M*K
                # output_size = N*M
                # x1.append(entry_2[0][3])
                # x2.append(N)
                # x3.append(K)
                # y.append((entry_2[0][1] - entry_1[0][1]))

        # get workload stats for given .txt file
        avg_diff = np.mean((stats_2/stats_1), axis=0)
        std_dev = np.std((stats_2/stats_1), axis=0)
        # print(f"Average difference: {avg_diff}")
        # print(f"Standard deviation: {std_dev}")

        tops_w_avg.append(avg_diff[0])
        tops_w_stddev.append(std_dev[0])
        gflops_avg.append(avg_diff[1])
        gflops_stddev.append(std_dev[1])
        util_avg.append(avg_diff[2])
        util_stddev.append(std_dev[2])

    # this output is used by fig12_2.py to create error_bar plots
    print(f"tops_w_avg = np.array({tops_w_avg})")
    print(f"tops_w_stddev = np.array({tops_w_stddev})")
    print(f"gflops_avg = np.array({gflops_avg})")
    print(f"gflops_stddev = np.array({gflops_stddev})")
    print(f"util_avg = np.array({util_avg})")
    print(f"util_stddev = np.array({util_stddev})")





