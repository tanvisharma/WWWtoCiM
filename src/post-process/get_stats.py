import re
from decimal import Decimal

"""
Post-processing wrapper to get the final TOPS/W, GFLOPs and Utilization. 

If the arch design is tensorcore-like,
 OPS/W = Energy/Total ops. GFLOPs and Utilization are the same as given in Summary stats. 

If the arch design is CiM,
 need a CIM primitive.txt file for the CiM specs
 Utilization scaling factor = (factors used in CiMStorage mapping)/(Rh*Ch) 
 Utilization = above scaling factor*Utilization from summary stats 
 
 ComputeCycles = Cycles from CiMUnit (from stats)*Latency (from cim-primitives.txt) 
 Final Cycles = ComputeCycles*BandwidthThrottlingfrom memory levels (from stats file) 
 GFLOPs = Total ops/Final Cycles 

 To consider intra-CimBank temporal reduction cost, find temporal reductions from summary stats,
 multiply this number by 0.05pJ, and add this to total energy
 ops/W = Total ops/this total energy 
"""

def get_summary_stats(stats):
    summary = stats[stats.index("Summary Stats") :]
    summary = summary.split("\n")
    summary = [x for x in summary if x != ""]

    for line in summary:
        if "Computes" in line:
            computes = int(line.split("=")[1])
        elif "GFLOPs" in line:
            gflops = float(line.split(":")[1])
        elif "Utilization" in line:
            utilization = float(line.split(":")[1].replace("%", ""))
        elif "Cycles" in line:
            cycles = int(line.split(":")[1])
        elif "Energy" in line:
            energy = float(line.split(":")[1].replace("uJ", "").replace(" ", ""))
        elif "EDP" in line:
            edp = float(line.split(":")[1])

    stats_dict = {
        "Computes": computes,
        "GFLOPs": gflops,
        "Utilization": utilization,
        "Cycles": cycles,
        "Energy": energy,
        "EDP": edp
    }

    return stats_dict

def get_energy_stats(stats):
    energy_stats = stats[stats.index("fJ/Compute") : ]
    energy_stats = energy_stats.split("\n")
    energy_stats = [x for x in energy_stats if x != ""]

    energy_entries = []
    for line in energy_stats:
        if "RF" in line:
            energy_entries.insert(0, float(line.split("=")[1].strip()))
        if "SMEM" in line:
            energy_entries.insert(0, float(line.split("=")[1].strip()))
        if "DRAM" in line:
            energy_entries.insert(0, float(line.split("=")[1].strip()))
        if "Total" in line:
            energy_entries.insert(0, float(line.split("=")[1].strip()))
    
    return energy_entries

def get_total_ops(stats):
    oper_stats = stats[stats.index("Operational Intensity Stats") : stats.index("Summary Stats")]
    oper_stats = oper_stats.split("\n")
    oper_stats = [x for x in oper_stats if x != ""]

    for line in oper_stats:
        if "Total ops" in line:
            return int(line.split(":")[1].strip())
        
def get_compute_cycles(stats):
    cimunit_stats = stats[stats.index("Level 0") : stats.index("Level 1")]
    cimunit_stats = cimunit_stats.split("\n")
    cimunit_stats = [x for x in cimunit_stats if x != ""]
    for line in cimunit_stats:
        if "Cycles" in line:
            return int(line.split(":")[1].strip())
        
def get_bw_throttling_factors(stats):
    # find all the matching regex with "Bandwidth Throttling : "
    factors = []
    for line in stats.split("\n"):
        if "Bandwidth throttling" in line:
            factors.append(float(line.split(":")[1].strip()))
    
    return factors

def get_util_factor(stats):
    cim_storage_stats = stats[stats.index("CiMStorage") : stats.index("CiMOutBuffer")]
    n_factor = 1
    k_factor = 1
    for line in cim_storage_stats.split("\n"):
        if "for N" in line:
            n_factor = int(line.split(":")[1].strip().replace(")", ""))
        if "for K" in line:
            k_factor = int(line.split(":")[1].strip().replace(")", ""))
    
    return k_factor, n_factor

def get_utilization(stats):
    mac_stats = stats[stats.index("Level 0") : stats.index("Level 1")]
    mac_stats = mac_stats.split("\n")
    total = 0
    used = 0
    for line in mac_stats:
        if "Instances" in line:
            total = int(line.split(":")[1].split("(")[0].strip())
        if "Utilized instances" in line:
            used = int(line.split(":")[1].strip())   
    return used/total

def calculate_new_cycles(stats, arithmetic_cycles):
    # Find the number of cycles for each level
    # print(arithmetic_cycles)
    levels = []
    for line in stats.split("\n"):
        if "Level" in line:
            levels.append(line)
    cycles = arithmetic_cycles
    for i,level in enumerate(levels):
        # print(level)
        if level in stats:
            if i == len(levels)-1:
                level_stats = stats[stats.index(level):]
            else:
                level_stats = stats[stats.index(level) : stats.index(levels[i+1])]
            level_stats = level_stats.split("\n")
            level_stats = [x for x in level_stats if x != ""]
            rd_bw = 1
            wr_bw = 1
            reads = 0
            writes = 0
            for line in level_stats:
                if "SMEM" in line:
                    rd_bw = 42 #TODO: read the bandwdith numbers from the stats file
                    wr_bw = 42
                if "DRAM" in line:
                    rd_bw = 32
                    wr_bw = 32
                if "Scalar reads" in line:
                    reads += int(line.split(":")[1].strip())
                if "Scalar updates" in line:
                    writes += int(line.split(":")[1].strip())
            # Find the number of cycles for this level
            memory_cycles = max(reads/rd_bw, writes/wr_bw)
            # print(memory_cycles)
            if memory_cycles > cycles:
                # print("Memory cycles are more than arithmetic cycles")
                cycles = memory_cycles

    return cycles

def dump_energy_stats(stats_path):
    # print(stats_path)
    stats_file = open(f"{stats_path}/timeloop-mapper.stats.txt").read()
    energy = get_energy_stats(stats_file)
    return energy

def dump_stats(stats_path, cim, cim_primitives_path):
    # print(stats_path)
    stats_file = open(f"{stats_path}/timeloop-mapper.stats.txt").read()
    stats = get_summary_stats(stats_file)
    total_ops = get_total_ops(stats_file)
    total_macs = stats["Computes"]
    if "tensor_core" in stats_path: #TODO: remove dependence on filename
        tops_w = (total_ops/stats["Energy"])*1e-6 #assuming energy is in uJ
        gflops = stats["GFLOPs"]
        utilization = get_utilization(stats_file) #False for non-cim architecture
        # stats["Utilization"] # this is the arithmetic ideal cycles/actual cycles, utilizaiton of the pipeline/not the hardware resources.
    else:
        # For energy, add cost of temporal reductions from levels other than CiM
        # Out of all the lines in stats, need "Temporal reductions (per-instance)"
        temporal_reductions = 0
        for line in stats_file.split("\n"):
            if "Temporal reductions" in line:
                temporal_reductions += float(line.split(":")[1].strip())
        
        temporal_reduction_energy = temporal_reductions * 0.05*1e-6 #0.05pJ/intadder 8bit
        # print(f"Temporal Reduction Energy: {temporal_reduction_energy}")

        total_energy = stats["Energy"] + temporal_reduction_energy
        tops_w = (total_ops/total_energy)*1e-6

        # For throughput, need cim-primitives.txt file
        cim_primitives = open(cim_primitives_path).read()
        # read the header and find the col for Rh, Ch, Latency
        header = cim_primitives.split("\n")[0].replace(" ","").split(",")
        rh_col = header.index("Rh")
        ch_col = header.index("Ch")
        latency_col = header.index("Latency")
        # read the values and find Rh, Ch, Latency
        values = cim_primitives.split("\n")
        for line in values:
            if cim in line: #assuming cim is the name of the primitive
                rh = int(line.split(",")[rh_col])
                ch = int(line.split(",")[ch_col])
                latency = int(line.split(",")[latency_col])
                break
        
        # Get Compute Cycles
        compute_cycles = get_compute_cycles(stats_file)
        # get the actual Rh and Ch from the stats file
        rh_used, ch_used = get_util_factor(stats_file)
        arithmetic_cycles = compute_cycles*(rh_used*ch_used)*latency

        new_cycles = calculate_new_cycles(stats_file, arithmetic_cycles)

        # bw_throttling_factors = get_bw_throttling_factors(stats_file)
        # bw_factor_tmp = 1
        # for factor in bw_throttling_factors:
        #     if factor == 0.00: #precision lost while prinitng stats.txt
        #         factor = 0.01
        #     bw_factor_tmp *= factor
        #     compute_cycles = compute_cycles/factor
        # new_cycles = compute_cycles * latency 
        gflops = (total_macs)/new_cycles #1GHz, because cycles are for mac

        # Get Utilization
        util_factor = rh_used*ch_used
        util_factor = (1/(rh*ch)) * util_factor
        utilization = util_factor * get_utilization(stats_file)

    # print(f"TOPS/W: {tops_w}")
    # print(f"GFLOPs: {gflops}")
    # print(f"Utilization: {utilization}")
    return float(tops_w), float(gflops), float(utilization)
# , bw_factor_tmp


           

def main():
    # dump_stats("../outputs/rf_compute_digital6T/GPT-J/outputs/2048_4096_4096", "digital6T", "../my-inputs/primitives/cim-primitives.txt")
    dump_stats("./../outputs/rf_compute_digital6T/all-gemms/outputs_consv2p1_isoarea/16_8192_8192", "digital6T", "../my-inputs/primitives/cim-primitives.txt")
    # dump_stats("./../outputs/rf_compute_analog8T/all-gemms/outputs_consv2p1_isoarea/64_64_64", "analog8T", "../my-inputs/primitives/cim-primitives.txt")
    # dump_stats("../outputs/rf_compute_analog8T/GPT-J/outputs/2048_4096_4096", "analog8T", "../my-inputs/primitives/cim-primitives.txt")
    # dump_stats("../outputs/tensor_core_like/GPT-J/outputs/2048_4096_4096", "tensor_core_like", "../my-inputs/primitives/cim-primitives.txt")
    return

if __name__ == "__main__":
    main()
