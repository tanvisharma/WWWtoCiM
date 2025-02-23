
# Script to generate bar plots given the gemm workloads and cim primitive

import argparse
import matplotlib.pyplot as plt
import os
from get_stats import dump_stats

CIM_PRIMITIVES_PATH = f"{os.curdir}/../my-inputs/primitives/cim-primitives.txt"
PRIMITIVE = "digital6T"
FIXED = "M"

# N=K, M changes
fig, axs = plt.subplots(3, 1, figsize=(5, 6))
count = 0
xaxis = []
num_bars = 0
# Define the labels
x_labels = [f'{2**i}' for i in range(4, 14)]
for i in range(4,14):
    N = 2**i
    K = 2**i
    num_bars  += 1
    tops_w = []
    gflops = []
    utilization = []
    for z in range(4, 14):
        M = 2**z
        xaxis.append(count)
        count += 1
        print(count)
        output_dir = f"{os.curdir}/../outputs/rf_compute_{PRIMITIVE}/all-gemms/outputs_consv2p1_isoarea/{M}_{N}_{K}"
        # gets tops/w, gflops and utilization for this workload shape
        entry = dump_stats(output_dir, PRIMITIVE, CIM_PRIMITIVES_PATH)
        tops_w.append(entry[0])
        gflops.append(entry[1])
        utilization.append(entry[2])
        # create 3 bar plots for each metric
        # 1. tops/w
        # 2. gflops
        # 3. utilization
    axs[0].bar(xaxis[count-10:count], tops_w)

    # axs[0].set_xlabel('X in GEMM(M,X,X)')
    axs[0].set_ylabel('TOPS/W')

    axs[1].bar(xaxis[count-10:count], gflops)
    # axs[1].set_xlabel('Problem size')
    axs[1].set_ylabel('GFLOPs')

    axs[2].bar(xaxis[count-10:count], utilization)
    # axs[2].set_xlabel('Problem size')
    axs[2].set_ylabel('Utilization')

# x_labels *= num_bars
# print(x_labels)
# print(xaxis)
# plt.xticks(xaxis, x_labels)
    # Set the labels for the x-axis
spaced_x_labels = ['' for i in range(len(xaxis))]
spaced_x_axis = []
for j in range(0, num_bars):
    # spaced_x_labels[j*10+5] = x_labels[j]
    spaced_x_axis.append(j*10+5)

# ... rest of your code ...

# Turn on the grid for each subplot
for ax in axs:
    ax.set_xticks(spaced_x_axis)
    ax.set_xticklabels(x_labels, rotation='vertical', fontsize=10)
    ax.grid(True)

# x axis of the bar plots
# plt.xlabel('(a) X in GEMM(M,X,X)', fontsize=10)
plt.tight_layout()
plt.savefig(f"bar_plots_{FIXED}_{PRIMITIVE}.png")


