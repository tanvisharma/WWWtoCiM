
# main file for finding the constraints given memory levels and constraints
# v0.1: Add multiple CiM primitives
# v0.2: Add hold factors from each CiM primitive
# v1.0: Updated the level names to match the architecture nodes
# v1.1: Updated the format for factors in the constraints dict, separate main function from mapping func
# v1.2: Add permutation constraints based on the value of loop factors
# v2.0: Divide N and K into multiple CiM primitives such that ~N and K are almost equally mapped~
# v2.1: Add threshold constraints while mapping X because mapping N and K equally does not produce the best results,
#       corrected the Threshold value based on experimental data
# v2.2: Separate the main function into get_mapping_constraints and reading input arguments

import argparse
import json

M_rem = 1
N_rem = 1
K_rem = 1

# Threshold decides whether to map N or K along different CiM primitives
# Kept 32 for SMEM, 4 for RF
THRESHOLD = 32

def improvise_N(capacity, M_used, N_used, K_used):
    A_size = K_used*M_used
    Z_size = N_used*M_used
    factor = 1
    while (A_size + Z_size <= capacity):
        N_factor = min_factor(N_rem//factor)
        if N_factor == None:
            break
        Z_size = N_factor*factor*Z_size
        factor *= N_factor

    if N_factor != None:
        #the last N_factor did not fit, so we need to go back one step
        factor = factor // N_factor
    
    return factor


def improvise_K(capacity, M_used, N_used, K_used):
    # Try to see if more dim of K can fit in the same memory
    A_size = K_used*M_used
    Z_size = N_used*M_used
    factor = 1
    while (A_size + Z_size <= capacity):
        K_factor = min_factor(K_rem//factor) # Find the smallest factor of remaining K that can fit in the memory
        if K_factor == None: # K is fully factored
            break
        A_size = K_factor*factor*A_size
        factor *= K_factor
    
    if K_factor != None:
        #the last K_factor did not fit, so we need to go back one step
        factor = factor // K_factor
    return factor


# assuming Smem only stores inputs, and outputs
def M_max_factor(capacity, M_used, N_used, K_used):
    # occupied capacity of SMEM is the sum of all the inputs, weights and outputs
    # for given Nc and Kc
    A_size = K_used*M_used
    Z_size = N_used*M_used
    M_max = (capacity)//(A_size + Z_size)
    M_factor = max_possible_factor(M_rem, M_max)
    return M_factor

def update_rem(dim, factor):
    # Update the remaining dimension after finding the factor
    return dim // factor

def min_factor(number):
    # find all factors and choose the minimum one
    for i in range(2, number + 1):
        if number % i == 0:
            return i #worst case returns the number

def max_possible_factor(dim, parallelism):
    # Find the maximum possible factor for a given dimension and parallelism
    factor = parallelism
    # check if the dimension is divisible by the parallelism
    while dim % factor != 0:
        factor -= 1
    return factor

def get_permutation(m, n, k):
    # based on the value of loop factors, decide the permutation
    # e.g. if m > n > k, then return "M, N, K"
    # total number of permutations = 6
    if m > n:
        if n > k:
            return "M, N, K"
        elif m > k:
            return "M, K, N"
        else:
            return "K, M, N"
    else:
        if n < k:
            return "K, N, M"
        elif m > k:
            return "N, M, K"
        else:
            return "N, K, M"

def get_bank_factors(X, N_rem, K_rem, N_cim_max, K_cim_max): #TODO: SImply the algorithm/code
    # Keep finding the factors of X until it is fully mapped
    X_rem = X
    K_bank_factor = 1
    N_bank_factor = 1
    map_K_first = True

    if (K_cim_max) > (N_cim_max):
        if (K_cim_max)/(N_cim_max) < THRESHOLD:
            map_K_first = True
        else:
            map_K_first = False
    else:
        if (N_cim_max)/(K_cim_max) < THRESHOLD:
            map_K_first = False
        else:
            map_K_first = True

    # Have to check if if it is possible to map K/N
    X_factor = min_factor(X_rem)
    if map_K_first:
        factor = max_possible_factor(K_rem, X_factor)
        if factor == 1:
            map_K_first = False
            factor = max_possible_factor(N_rem, X_factor)
            if factor == 1:
                return 1, 1
    else:
        factor = max_possible_factor(N_rem, X_factor)
        if factor == 1:
            map_K_first = True
            factor = max_possible_factor(K_rem, X_factor)
            if factor == 1:
                return 1, 1

    while (X_rem > 1):
        X_factor = min_factor(X_rem)

        if map_K_first:
            K_factor = max_possible_factor(K_rem//K_bank_factor, X_factor)
            if K_factor == 1: #can't increase K factor
                    break #also check if the threshold is crossed
            if (K_cim_max*K_bank_factor) >= THRESHOLD*(N_cim_max*N_bank_factor):
                    break
            K_bank_factor *= K_factor
        else:
            N_factor = max_possible_factor(N_rem//N_bank_factor, X_factor)
            if N_factor == 1: #can't increase N factor
                break 
            if (N_cim_max*N_bank_factor) >= THRESHOLD*(K_cim_max*K_bank_factor):
                break
            N_bank_factor *= N_factor
        
        X_rem = X_rem // X_factor

    return K_bank_factor, N_bank_factor

def get_bank_factors_X(X, map_K_first, rem, N_cim_max, K_cim_max): #TODO: when X > 1
    # Keep finding the factors of X until it is fully mapped
    X_rem = X
    bank_factor = 1

    while (X_rem > 1):
        X_factor = min_factor(X_rem)

        # this works only when there is a possibility to map both K and N across CiM primitives
        # K_cim_max > N_cim_max and K_cim_max/N_cim_max < THRESHOLD
        # if (K_cim_max*K_bank_factor) > (N_cim_max*N_bank_factor):
        #     if (K_cim_max*K_bank_factor)/(N_cim_max*N_bank_factor) < THRESHOLD:
        #         map_K_first = True
        #     else:
        #         map_K_first = False
        # else:
        #     if (N_cim_max*N_bank_factor)/(K_cim_max*K_bank_factor) < THRESHOLD:
        #         map_K_first = False
        #     else:
        #         map_K_first = True
        
        if map_K_first:
            running_factor = max_possible_factor(rem//bank_factor, X_factor)
            if running_factor == 1: #can't increase K factor
                break #also check if the threshold is crossed
            if (K_cim_max*bank_factor) >= THRESHOLD*(N_cim_max):
                break
            bank_factor *= running_factor
        else:
            running_factor = max_possible_factor(rem//N_bank_factor, X_factor)
            if running_factor == 1: #can't increase N factor
                break 
            if (N_cim_max*bank_factor) >= THRESHOLD*(K_cim_max):
                break
            bank_factor *= running_factor
        
        X_rem = X_rem // X_factor

    return bank_factor




def get_mapping_constraints(M, N, K, Rp, Cp, Rh, Ch, X, Y, Smem: int = -1):

    # Set globals
    global M_rem, N_rem, K_rem
    if Smem != -1:
        num_memory_levels = 2 # +1 for DRAM
        constraints = {
            "DRAM": [None],
            "SMEM" : [None],
            "CiMBank": [None],
            "CiMArray": [None],
            "CiMStorage": [None],
            "permutation": [None]
        }
    else:
        num_memory_levels = 1
        constraints = {
            "DRAM": [None],
            "CiMBank": [None],
            "CiMArray": [None],
            "CiMStorage": [None],
            "permutation": [None]
        }
    
    M_rem = M
    N_rem = N
    K_rem = K
    print(f"Start: {M_rem}, {N_rem}, {K_rem}")

    # ----------------------- #
    # Decide arithmetic levels constraint
    Nc = max_possible_factor(N_rem, Cp)
    Kc = max_possible_factor(K_rem, Rp)
    constraints["CiMArray"] = [f'M={1}', f'N={Nc}', f'K={Kc}']
    
    # update remaining values of N and K
    N_rem = N_rem // Nc
    K_rem = K_rem // Kc
    print(f"After CiM Parallel: {M_rem}, {N_rem}, {K_rem}")

    # Have to decide whether map the remaining weights to multiple banks (parallel) or inside the same bank (Rh, Ch)
    # In our algorithm, we prioritize parallelism over Rh, Ch

    # either of the N or K dimension can be parallelized across multiple CiM Banks depending on the Threshold value
    # find the shape of CiM primitive based on Rh, Ch and Rp, Cp
    K_cim_max = Rh*Rp
    N_cim_max = Ch*Cp
    K_bank_factor, N_bank_factor = get_bank_factors(Y, N_rem, K_rem, N_cim_max, K_cim_max)

    # TODO: if X dimension is > 1, then map the other dimension to this axis
    # if X > 1:
    #     N_cim_max *= N_bank_factor_Y
    #     K_cim_max *= K_bank_factor_Y
    #     if 
    
    print(f"After mapping Y, K_bank_factor: {K_bank_factor}, N_bank_factor: {N_bank_factor}")

    # Nsp = max_possible_factor(N_rem, X)
    # Ksp = max_possible_factor(K_rem, Y)
    constraints["CiMBank"] = [f'M={1}', f'N={N_bank_factor}', f'K={K_bank_factor}']

    # update remaining values of N and K
    N_rem = N_rem // N_bank_factor
    K_rem = K_rem // K_bank_factor
    print(f"After CiMBank: {M_rem}, {N_rem}, {K_rem}")


    # map the remaining dims of weights (N_rem, K_rem) to the same bank (Rh, Ch) to maximize utilization
    Nh = max_possible_factor(N_rem, Ch)
    Kh = max_possible_factor(K_rem, Rh)
    constraints["CiMStorage"] = [f'M={1}', f'N={Nh}', f'K={Kh}']

    # update remaining values of N and K
    N_rem = N_rem // Nh
    K_rem = K_rem // Kh
    print(f"After CiM Hold: {M_rem}, {N_rem}, {K_rem}")

    
    # After CiM banks, find the maximum factors that can fit in the next memory level
    # Decide memory levels constraint
    permutation_smem = None
    if num_memory_levels == 2:
        # Smem is given
        Smem = Smem*1024 # KB
        M_used, N_used, K_used = M//M_rem, N//N_rem, K//K_rem
        M1 = M_max_factor(Smem, M_used, N_used, K_used)
        K1 = improvise_K(Smem, M1, N_used, K_used)
        N1 = improvise_N(Smem, M1, N_used, K_used*K1)
        M_rem = M_rem // M1
        N_rem = N_rem // N1
        K_rem = K_rem // K1
        print(f"After Smem: {M_rem}, {N_rem}, {K_rem}")
        constraints['SMEM'] = [f'M={M1}', f'N={N1}', f'K={K1}']
        permutation_smem = get_permutation(M1, N1, K1)


    # Testing with 1 CiM primitve only runs
    # constraints["CiMBank"] = [f'M={1}', f'N={1}', f'K={1}']
    # # constraints["CiMStorage"] = [f'M={1}', f'N={1}', f'K={1}']

    # Get DRAM level constraints
    constraints["DRAM"] =[f'M={M_rem}', f'N={N_rem}', f'K={K_rem}']
    permutation_dram = get_permutation(M_rem, N_rem, K_rem)

    # kind of assertion checks to ensure rem values are correct
    M_rem = M_rem // M_rem
    N_rem = N_rem // N_rem
    K_rem = K_rem // K_rem
    print(f"After DRAM: {M_rem}, {N_rem}, {K_rem}")

    constraints["permutation"] = [permutation_dram, permutation_smem]

    return constraints

def main():
    parser = argparse.ArgumentParser(description='Run Mapping constraint algorithm with given GEMM shape and CiM configuration.')
    parser.add_argument('--M', type=int, default=16,  help='Input M.')
    parser.add_argument('--N', type=int, default=16,  help='Input N.')
    parser.add_argument('--K', type=int, default=16,  help='Input K.')
    parser.add_argument('--Rp', type=int, default=64,  help='CiM primitive Rp.')
    parser.add_argument('--Cp', type=int, default=4,  help='CiM primitive Cp.')
    parser.add_argument('--Rh', type=int, default=1,  help='Cim primitive Rh.')
    parser.add_argument('--Ch', type=int, default=16,  help='CiM primitive Rp.')
    parser.add_argument('--X', type=int, default=1,  help='Number of CiM primitives in CiMBank X.')
    parser.add_argument('--Y', type=int, default=4,  help='Number of CiM primitives in CiMBank Y.')
    parser.add_argument('--Smem', type=int, default=256,  help='SMEM Size')

    args = parser.parse_args()

    #Print all arguments
    print("Arguments:", args)

    constraints = get_mapping_constraints(args.M, args.N, args.K, args.Rp, args.Cp, args.Rh, args.Ch, args.X, args.Y, args.Smem)

    # Write constraints to a file
    # Create a dictionary with the constraints and the input arguments
    output = {
        "input_arguments": vars(args),
        "constraints": constraints,
    }
    print(output)

    # Serialize the output dictionary into a JSON formatted string
    output_str = json.dumps(output)

    # Write the output string to the output.jsonl file
    with open('output.jsonl', 'a') as f:
        f.write(output_str + '\n')


    return

if __name__ == "__main__":
    main()
