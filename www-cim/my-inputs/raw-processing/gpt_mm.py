import requests
import json

def fetch_config(model_path):
    url = f"https://huggingface.co/{model_path}/raw/main/config.json"
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an exception for HTTP error codes
        return response.json()  # Try to decode JSON
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP Error: {e}")
    except requests.exceptions.ConnectionError as e:
        raise Exception(f"Connection Error: {e}")
    except requests.exceptions.Timeout as e:
        raise Exception(f"Timeout Error: {e}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error Fetching: {e}")
    except ValueError as e:
        raise Exception(f"Invalid JSON: {e}")


def calculate_gpt_matrix_sizes(config):
    hidden_size = config['n_embd']
    intermediate_size = 16384 # gpt-j, not included in config.json
    max_position_embeddings = config['n_positions']

    matrix_sizes = []
    # Q calculations
    q_size = (1, hidden_size, hidden_size) # because 1 token processed at a time 

    # [M,N,K] Sizes for K, V calculations
    kv_size = (max_position_embeddings, hidden_size, hidden_size)  # 2 separate matrices

    # Q * K^T (attention score matrix before softmax)
    attention_scores = (1, max_position_embeddings, hidden_size)

    # (Q * K^T) * V
    weighted_sum = (1, hidden_size, max_position_embeddings)

    # Output of self-attention - same as QKV
    attention_output = (1, hidden_size, hidden_size)

    # FF1
    ffn_first = (1, intermediate_size, hidden_size)

    # FF2
    ffn_second = (1, hidden_size, intermediate_size)

    matrix_sizes.append(q_size)
    matrix_sizes.append(kv_size)
    matrix_sizes.append(attention_scores)
    matrix_sizes.append(weighted_sum)
    matrix_sizes.append(ffn_first)
    matrix_sizes.append(ffn_second)

    return matrix_sizes


def write_to_file(model_name, matrix_sizes):
    filename = f"{model_name}_matrix_sizes.txt"
    with open(filename, 'w') as file:
        for idx, sizes in enumerate(matrix_sizes, 1):
            # sizes are in a tuple
            file.write(f"{sizes}\n")
    print(f"Matrix sizes written to {filename}")

def main(model_path):
    config = fetch_config(model_path)
    if 'gpt-j' in model_path:
        matrix_sizes = calculate_gpt_matrix_sizes(config)
    # else:
        # matrix_sizes = calculate_matrix_sizes(config)
    # model_name = config['model_type']
    model_name = model_path.split('/')[1]
    write_to_file(model_name, matrix_sizes)

# Example Usage
model_name_path = "EleutherAI/gpt-j-6b"

main(model_name_path)
