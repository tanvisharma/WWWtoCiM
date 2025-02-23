
# Given a CiM Primitive type, this script generates the TOPS/W vs GFLOPs for given workloads.


import argparse
import os
from typing import Optional
import numpy as np
import csv
import matplotlib.pyplot as plt
from get_stats import dump_stats

CIM_PRIMITIVES_PATH = f"{os.curdir}/../my-inputs/primitives/cim-primitives.txt"

def plot(primitive, workloads):
    markers = ["x", "o", "s", "D", "^", "v", ">", "<", "p", "h", "H", "*", "d", "P", "X", "|", "_"] # old code generated all sub-plots in one figure
    # colors = ['tab:orange', 'tab:brown', 'tab:olive', 'tab:cyan', 'tab:purple', 'tab:pink', 'tab:red', 'tab:blue', 'tab:green', 'tab:gray', 'tab:orange', 'tab:brown', 'tab:olive', 'tab:cyan', 'tab:purple', 'tab:pink', 'tab:red', 'tab:blue', 'tab:green', 'tab:gray']
    colors = ['tab:red', 'tab:brown', 'tab:olive', 'tab:cyan', 'tab:purple', 'tab:pink', 'tab:red', 'tab:blue', 'tab:green', 'tab:gray', 'tab:orange', 'tab:brown', 'tab:olive', 'tab:cyan', 'tab:purple', 'tab:pink', 'tab:red', 'tab:blue', 'tab:green', 'tab:gray']
    
    plt.figure(figsize=(5,5))

    for workload in workloads:
        stats_1 = np.array([])
        algo_reuse = np.array([])
        macs_list = np.array([])
        labels = []
        with open(workload, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            next(reader)
            for row in reader:
                modelname = row[0]
                M = row[1]
                N = row[2]
                K = row[3]

                labels.append(f"{M},{N},{K}")
                # labels.append(f"{M}")
                # size = np.log2(int(M))*5 + 10
                # print(size)
                output_dir = f"{os.curdir}/../outputs/rf_compute_{primitive}/{modelname}/outputs_consv2p1_isoarea/{M}_{N}_{K}"

                entry_1 = dump_stats(output_dir, primitive, CIM_PRIMITIVES_PATH)
                entry_1 = np.array(entry_1).reshape(1, -1)

                if stats_1.size == 0:
                    stats_1 = entry_1
                else:
                    stats_1 = np.vstack((stats_1, entry_1))
                M = int(M)
                N = int(N)
                K = int(K)
                # reuse = (M*N*K)/(M*K + N*K + M*N)
                # macs = M*N*K
                # macs_list = np.append(macs_list, macs)
                
                # algo_reuse.append(macs)
    
        # if comparison_type == "TOPS/W vs GFLOPs":
        # print(algo_reuse)
        # print(max(algo_reuse))
        # normalized_reuse = [float(x/np.mean(macs_list))*80 for x in macs_list]
        # plt.scatter(stats_1[:, 1], stats_1[:, 0], label=workload, marker=markers.pop(0))
        name = workload.split("/")[-1].split(".")[0]
        plt.scatter(stats_1[:, 1], stats_1[:, 0], marker=markers.pop(0), color=colors.pop(0), label=name)#, s=size)

        if workload == "../my-inputs/workloads/Mgemms-128.txt" or workload == "../my-inputs/workloads/Mgemms-64.txt":
            if args.annotate:
                for i, txt in enumerate(labels):
                    if txt == "2048":
                        y_offset = 20
                    elif txt == "4096":
                        y_offset = 5
                    elif txt == "8192":
                        y_offset = 25
                    else:
                        y_offset = 1
                    # if txt == "4096":
                    #     y_offset = 5

                    plt.annotate(txt, (stats_1[i, 1], stats_1[i, 0]), fontsize=6
                    , xytext=(y_offset, 1),  # Offset from the actual point (x, y) in points
            textcoords='offset points') #move the annotation away from each other

        
    # plt.legend(ncol=len(workloads)/2, loc="upper left", fontsize=6)
    plt.grid(True)
    plt.xlabel("GFLOPs", weight="bold", fontsize=12)
    plt.ylabel("TOPS/W", weight="bold", fontsize=12)
    plt.show()
    figname = f"{primitive}_workloads.png"
    plt.savefig(figname)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare results from different output directories")
    parser.add_argument("--primitive", default="analog6T", help="Name of the first primitive to compare")
    parser.add_argument("--workloads", default="../my-inputs/workloads/all-gemms.txt", type=str, help="Name of all the workload .txt files to compare results")
    parser.add_argument("--annotate", type=bool, help="if you want to annotate the points")
    args = parser.parse_args()

    workloads = args.workloads.split(" ")
    plot(args.primitive, workloads)
