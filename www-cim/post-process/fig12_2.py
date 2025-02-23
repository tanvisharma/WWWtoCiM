import matplotlib.pyplot as plt
import numpy as np

# labels =  ['Regular', 'BERT', 'GPT-J', 'ResNet']
labels =  ['BERT', 'GPT', 'ResNet', 'DLRM']

# CONS vs non-CONS
tops_w_avg = np.array([1.2929231871704296, 1.1450250360740135, 1.192195998592496, 1.1860945390323105])
tops_w_stddev = np.array([0.3285010799191619, 0.2619907718000543, 0.29614336829130694, 0.293346531199289])
gflops_avg = np.array([5.2, 3.193048724014639, 4.362680917445263, 4.275220961580089])
gflops_stddev = np.array([2.4000000000000004, 2.578078893211173, 2.56047240422877, 2.567667575090551])
util_avg = np.array([6.933333333333333, 8.484848484848484, 6.601092896174862, 7.11111111111111])
util_stddev = np.array([3.2, 4.932603624091104, 3.7383226835319325, 5.844949381692232])

# RF vs Tensorcore
# tops_w_avg = np.array([3.0143863809432974, 2.1442373535040833, 2.4853212712027766, 2.4407507096232965])
# tops_w_stddev = np.array([0.09595131521112821, 0.9702755226012435, 0.6710354216733447, 0.7046865056416342])
# gflops_avg = np.array([1.3805983425680328, 0.979874380336581, 1.6766820152398278, 1.6393504516575448])
# gflops_stddev = np.array([0.008460879691183355, 0.43813980424248833, 1.517192069325276, 1.5070841631799359])
# util_avg = np.array([0.6666666666666666, 0.7878787878787878, 0.7066399134790529, 0.7053709215167547])
# util_stddev = np.array([0.0, 0.25712973861328997, 0.4879402536091185, 0.4801838508037892])

# # SMEM vs Tensorcore
# tops_w_avg = np.array([3.30181699829087, 2.317751275606085, 2.6085930241174475, 2.5601284150110057])
# tops_w_stddev = np.array([0.11446295560155142, 1.1340449969312358, 0.6471628787224536, 0.6907698995371399])
# gflops_avg = np.array([14.398655040795589, 8.212477985951976, 8.34876461725622, 8.099620907578178])
# gflops_stddev = np.array([1.2040430918826779, 7.099395301127954, 5.23321785292258, 5.330137722661364])
# util_avg = np.array([0.6666666666666666, 0.7878787878787878, 0.5230977487477233, 0.513105227623457])
# util_stddev = np.array([0.0, 0.25712973861328997, 0.5659185464556048, 0.5600340773198728])


fig, axs = plt.subplots(1, 3, figsize=(12, 5))

# Plot for TOPS/W
axs[0].errorbar(labels, tops_w_avg, yerr=tops_w_stddev, fmt='o', capsize=10, linewidth=6, markersize=16, color='tab:green')
axs[0].set_xlabel('(a)', fontsize=20, weight='bold')
axs[0].set_ylabel('Change (x) in TOPS/W', fontsize=16, weight='bold')

# Plot for GFLOPs
axs[1].errorbar(labels, gflops_avg, yerr=gflops_stddev, fmt='o', capsize=10, linewidth=6, markersize=16, color='tab:blue')
axs[1].set_xlabel('(b)', fontsize=20, weight='bold')
axs[1].set_ylabel('Change (x) in GFLOPs', fontsize=16, weight='bold')

# Plot for Utilization
axs[2].errorbar(labels, util_avg, yerr=util_stddev, fmt='o', capsize=10, linewidth=6, markersize=16, color='tab:orange')
axs[2].set_xlabel('(c)', fontsize=20, weight='bold')
axs[2].set_ylabel('Change (x) in Utilization', fontsize=16, weight='bold')

for ax in axs:
    ax.set_xticklabels(labels, rotation=90, weight='bold')
    for label in ax.get_yticklabels():
        label.set_weight("bold")
    ax.axhline(0, color='black', linewidth=0.5)
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.grid(True)

plt.tight_layout()
plt.savefig("error_bar_plots.png")

