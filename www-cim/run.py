from typing import Optional
import os
import timeloopfe.v4 as tl
from timeloopfe.v4.constraints import Factors, Permutation, Temporal, Spatial
import json
import csv
import argparse
import subprocess
from constraints.main import get_mapping_constraints

Specification = tl.Specification


# Define relative paths
MAIN_DIR = os.curdir
COMPONENTS_PATH = f"{MAIN_DIR}/designs/_components/components.yaml"
CIM_PATH = f"{MAIN_DIR}/designs/_components/cimmac.yaml"
PROBLEM_PATH = f"{MAIN_DIR}/designs/_include/mm-example.yaml"
MAPPER_PATH = f"{MAIN_DIR}/designs/_include/mapper.yaml"


def update_arch(spec: tl.Specification, name, rp:int, cp:int, rh:int, ch:int, X:int, Y:int):
    spec.variables["cimtype"] = f"'{name}'"
    spec.variables["Rp"] = rp
    spec.variables["Cp"] = cp
    spec.variables["Rh"] = rh
    spec.variables["Ch"] = ch
    spec.variables["X"] = X
    spec.variables["Y"] = Y

    # update the def constraints in the spec for CiMStorage, CiMArray and CiMBank
    tmp = spec.constraints.targets
    for i,entry in enumerate(tmp):
        if entry.target == 'CiMStorage' and type(spec.constraints.targets[i]) == Temporal:
            spec.constraints.targets[i].factors.add_leq_factor("N", ch, True)
            spec.constraints.targets[i].factors.add_leq_factor("K", rh, True)
        if entry.target == 'CiMArray' and type(spec.constraints.targets[i]) == Spatial:
            spec.constraints.targets[i].factors.add_leq_factor("N", cp, True)
            spec.constraints.targets[i].factors.add_leq_factor("K", rp, True)
        if entry.target == 'CiMBank' and type(spec.constraints.targets[i]) == Spatial:
            spec.constraints.targets[i].factors.add_leq_factor("K", X, True)
            spec.constraints.targets[i].factors.add_leq_factor("N", Y, True)

    return


def update_cons(spec: tl.Specification, M:int, N:int, K:int, SMEM_size:int=-1):
    # get the CiM characteristics from the spec
    rp = int(spec.variables["Rp"])
    cp = int(spec.variables["Cp"])
    rh = int(spec.variables["Rh"])
    ch = int(spec.variables["Ch"])
    X = int(spec.variables["X"])
    Y = int(spec.variables["Y"])

    # call constraint algorithm with these parameters to get the mapping constraints
    # check if SMEM present in the specs
    mapping = {}
    mapping = get_mapping_constraints(M, N, K, rp, cp, rh, ch, X, Y, SMEM_size)

    if mapping is None:
        print(f"*** ERROR ***: Mapping constraints not found for {M}x{N}x{K}.")
        return
    else:
        replace_constraints(mapping, spec, M, N, K)
    return


def replace_constraints(mapping, spec: tl.Specification, M:int, N:int, K:int):
    tmp = spec.constraints.targets
    # update this to go over the list of all targets instead of relying on the order
    for i,entry in enumerate(tmp):
        if entry.target == 'DRAM':
            # check that the factors are temporal constraints
            if type(spec.constraints.targets[i]) == Temporal:
                spec.constraints.targets[i].factors = Factors.factory(mapping["DRAM"]) #DRAM temporal constraints
                spec.constraints.targets[i].permutation = Permutation.factory(mapping["permutation"][0])
                    # "M, K, N")
        if entry.target == 'SMEM':
            # check that the factors are temporal constraints
            if type(spec.constraints.targets[i]) == Temporal:
                spec.constraints.targets[i].factors = Factors.factory(mapping["SMEM"]) #SMEM temporal constraints
                spec.constraints.targets[i].permutation = Permutation.factory(mapping["permutation"][1])
                # spec.constraints.targets[i].permutation = Permutation.factory("M, K, N")
        if entry.target == 'CiMStorage':
            # check that the factors are temporal constraints
            if type(spec.constraints.targets[i]) == Temporal:
                spec.constraints.targets[i].factors = Factors.factory(mapping["CiMStorage"])
                spec.constraints.targets[i].permutation = Permutation.factory("M, K, N")
        if entry.target == 'CiMArray':
            # check that the factors are spatial constraints
            if type(spec.constraints.targets[i]) == Spatial:
                spec.constraints.targets[i].factors = Factors.factory(mapping["CiMArray"])
        if entry.target == 'CiMBank':
            # check that the factors are spatial constraints
            if type(spec.constraints.targets[i]) == Spatial:
                spec.constraints.targets[i].factors = Factors.factory(mapping["CiMBank"])

    return 


def remove_sparse_optimizations(spec: tl.Specification):
    """This function is used by some Sparseloop tutorials to test with/without
    sparse optimizations"""
    for s in spec.get_nodes_of_type(
        (
            tl.sparse_optimizations.ActionOptimizationList,
            tl.sparse_optimizations.RepresentationFormat,
            tl.sparse_optimizations.ComputeOptimization,
        )
    ):
        s.clear()
    return spec


def run_mapper(args):
    # Gather .yaml files needed to run the mapper
    # -- Architecture file --
    arch_dir = args.arch
    arch_path = f"{arch_dir}/arch_split.yaml"
    arch_design = os.path.basename(os.path.normpath(arch_dir))
    
    if not os.path.exists(arch_path):
        print(f"Architecture file {arch_path} does not exist.")
        return
    
    # -- Mapper Specification --
    spec = tl.Specification.from_yaml_files(
                arch_path,
                COMPONENTS_PATH,
                MAPPER_PATH,
                PROBLEM_PATH,
                CIM_PATH,
    )

    # Used without sparse optimizations
    remove_sparse_optimizations(spec)

    # -- Problem file --
    problems_list = []
    if args.gemms is not None:
        gemms = []
        with open(args.gemms, 'r') as f:
            gemms = list(csv.reader(f, delimiter='\t'))

        gemms = gemms[1:]
        
        for gemm in gemms:
            modelname, m, n, k, *_ = gemm
            problems_list.append((modelname, m, n, k))
    
    else:
        problems_list.append(("GEMMs", args.M, args.N, args.K))


    # -- Run the mapper for each design point--
    for gemm_specs in problems_list:
            
        modelname, m, n, k = gemm_specs
        problem = f"{m}_{n}_{k}"
        m = int(m)
        n = int(n)
        k = int(k)
        # Update the Specification with given problem size
        spec.problem.instance["M"] = m
        spec.problem.instance["N"] = n
        spec.problem.instance["K"] = k

        if "tensor" in arch_design:
            # Optional TODO: update the X and Y mesh dimensions in spec
            output_dir = f"{os.curdir}/outputs/{arch_design}/{modelname}/outputs/{problem}"
            if os.path.exists(output_dir):
                print(f"Output directory {output_dir} already exists. Deleting...")
                os.system(f"rm -rf {output_dir}")
            os.makedirs(output_dir, exist_ok=True)

            print(f"\n\nRunning mapper for arch {arch_design}, problem {m},{n},{k} in {output_dir}...")
            tl.call_mapper(
                spec,
                output_dir=output_dir,
                dump_intermediate_to=output_dir,
            )
            if not os.path.exists(f"{output_dir}/timeloop-mapper.stats.txt"): #stop running
                exit(f"ERROR:"
                f"Mapper did not generate expected output for {arch_path}. "
                f"Please check the logs for more details."
                )

        else:
            if args.cim_list == None:
                # run the mapper with the default cim primitive
                 # -- Output directory --
                if args.cons == True:
                    if "smem" in arch_design: #TODO: remove dependence on arch name
                        update_cons(spec, m, n, k)
                    else:
                        # get smem size from the spec
                        smem_size = spec.architecture.nodes[2].attributes.width # in KB, TODO: remove dependence on order
                        update_cons(spec, m, n, k, smem_size)
                    output_dir = f"{os.curdir}/outputs/{arch_design}/{modelname}/outputs_{args.name}/{problem}"
                else:
                    output_dir = f"{os.curdir}/outputs/{arch_design}/{modelname}/outputs/{problem}"

                # Set up output directory
                if os.path.exists(output_dir):
                    print(f"Output directory {output_dir} already exists. Deleting...")
                    os.system(f"rm -rf {output_dir}")
                os.makedirs(output_dir, exist_ok=True)

                print(f"\n\nRunning mapper for arch {arch_design}, problem {m},{n},{k} in {output_dir}...")

                tl.call_mapper(
                    spec,
                    output_dir=output_dir,
                    dump_intermediate_to=output_dir,
                )

                if not os.path.exists(f"{output_dir}/timeloop-mapper.stats.txt"): #stop running
                    exit(f"ERROR:"
                    f"Mapper did not generate expected output for {arch_path}. "
                    f"Please check the logs for more details."
                    )

            else:
                # Check that a list of CiM primitives are given.
                if not os.path.exists(args.cim_list):
                    print(f"*** ERROR ***: {problem}: CIM primitives list file {args.cim_list} \
                            does not exist for {arch_design}.")
                    return

                with open(args.cim_list, 'r') as file:
                    cim_list = [line.strip() for line in file]

                    cim_list = cim_list[1:] # skip the header
                    for cim in cim_list:
                        name, rp, cp, rh, ch, *_ = cim.split(",")
                        update_arch(spec, name, rp, cp, rh, ch, args.X, args.Y)
                
                        # Update the Specification with autogenerated constraints
                        if args.cons == True:
                            if "rf" in arch_design: #TODO: remove dependence on arch name
                                # get smem size from the spec
                                smem_size = spec.architecture.nodes[2].attributes.width # in KB, TODO: remove dependence on order
                                update_cons(spec, m, n, k, smem_size)
                            else:
                                update_cons(spec, m, n, k)

                        # -- Output directory --
                        if args.cons == True:
                            output_dir = f"{os.curdir}/outputs/{arch_design}_{name}/{modelname}/outputs_{args.name}/{problem}"
                        else:
                            output_dir = f"{os.curdir}/outputs/{arch_design}_{name}/{modelname}/outputs/{problem}"

                        print(f"\n\nRunning mapper for arch {arch_design}, problem {m},{n},{k} in {output_dir}...")
                        tl.call_mapper(
                            spec,
                            output_dir=output_dir,
                            dump_intermediate_to=output_dir,
                        )
                        if not os.path.exists(f"{output_dir}/timeloop-mapper.stats.txt"): #stop running
                            exit(f"ERROR:"
                            f"Mapper did not generate expected output for {arch_path}. "
                            f"Please check the logs for more details."
                            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process architecture and input shape constraints to run timeloopfe.')
    parser.add_argument('--M', type=int, default=16,  help='Input M when running for a single GEMM shape.')
    parser.add_argument('--N', type=int, default=16,  help='Input N when running for a single GEMM shape.')
    parser.add_argument('--K', type=int, default=16,  help='Input K when running for a single GEMM shape.')
    parser.add_argument('--gemms', type=str, default=None, help='Path to .txt file containing GEMM sizes.')
    parser.add_argument('--arch', type=str, default="./designs/example/", help='Architecture directory containing arch_split.yaml. Options: ./designs/rf_compute, ./designs/smem_compute, ./designs/tensor-core-like')  #default/rf/smem
    parser.add_argument('--X', type=int, default=1, help='Number of CiM primitives in X dimension. Current constraint algo only maps along Y dimension.')
    parser.add_argument('--Y', type=int, default=4, help='Number of CiM primitives in Y dimension.')
    parser.add_argument('--cim_list', type=str, default=None, help='Path to .txt file containing list of CiM primitives (type, Rp, Cp, Rh, Ch, etc.). Check my-inputs/primitives/ for sample files.')
    parser.add_argument('--cons', type=bool, default=False, help='Option to use our mapping constraint algorithm for CiM primitive architecture. Does not work for tensor-core-like') 
    parser.add_argument('--name', type=str, default="cons", help='Postfix for output directory name.') 
    parser.add_argument('--model', type=bool, default=False, help='Option to run Timeloop Model instead of mapper. Not supported at the moment.')  #TODO: Add support for timeloop model, require changes in timeloopfe

    args = parser.parse_args()
    run_mapper(args)
