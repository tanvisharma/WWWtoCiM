
# For a given arch design, plot the bar chart for different workloads with a mean line passing through each workload

from get_stats import dump_stats
import os
import matplotlib.pyplot as plt

workloads_path = ['../inputs/bert.txt', '../inputs/gptj.txt', '../inputs/resnet.txt', '../inputs/dlrm.txt']
workloads = ["BERT-Large", "GPT-J", "ResNet50", "DLRM"]
PRIMITIVE = "digital6T"
# PRIMITIVE = "tensor_core_like"
LEVEL = "smem"
CIM_PRIMITIVES_PATH = f"../my-inputs/primitives/cim-primitives.txt"

x_labels = []
count = 0
xaxis = []
fig, axs = plt.subplots(1, 3, figsize=(20, 5))
for i, workload in enumerate(workloads):
    path = workloads_path[i]
    if PRIMITIVE == "tensor_core_like":
        workload_dir = f"../outputs/{PRIMITIVE}/{workload}/outputs/"
    else:
        # workload_dir = f"../outputs/{LEVEL}_compute_{PRIMITIVE}/{workload}/outputs_consv2p1_isoarea/"
        workload_dir = f"../outputs/{LEVEL}_compute_{PRIMITIVE}/{workload}/outputs_consv2p1_isocap/"
    # for all outputs in this dir
    topsw_list = []
    gflops_list = []
    util_list = []
    localcount = 0
    for root, dirs, files in os.walk(workload_dir):
        for dir in dirs:
            xaxis.append(count)
            count += 1
            localcount += 1
            name = dir.replace("_", ",")
            x_labels.append(name)
            output_dir = os.path.join(root, dir)
            topsw, gflops, util = dump_stats(output_dir, PRIMITIVE, CIM_PRIMITIVES_PATH)
            # print(f"{output_dir}: {topsw}")
            print(f"{gflops}")
            topsw_list.append(topsw)
            gflops_list.append(gflops)
            util_list.append(util)

    axs[0].bar(xaxis[count- localcount: count], topsw_list, label=workload)
    axs[0].set_ylabel('TOPS/W', weight="bold", fontsize=18)
    axs[1].bar(xaxis[count- localcount: count], gflops_list, label=workload)
    axs[1].set_ylabel('GFLOPs', weight="bold", fontsize=18)
    axs[2].bar(xaxis[count- localcount: count], util_list, label=workload)
    axs[2].set_ylabel('Utilization', weight="bold", fontsize=18)

# axs[0].set_ylim([0,2.2])
# Set the labels for the x-axis
print(x_labels)
for ax in axs:
    ax.set_xticks(xaxis)
    ax.tick_params(axis='y', labelsize=18) 
    ax.set_xticklabels(x_labels, rotation=90, fontsize=16)
    ax.grid(True)
    # ax.legend(ncol=len(workloads), loc="upper center", fontsize=8)
plt.tight_layout()
plt.savefig(f"workloads_{LEVEL}_{PRIMITIVE}_isoarea.png")
# plt.savefig(f"check_{LEVEL}_{PRIMITIVE}_isoarea.png")
