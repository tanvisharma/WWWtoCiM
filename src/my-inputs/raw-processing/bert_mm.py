import torch
from transformers import AutoModel, AutoTokenizer

def attention_hook(module, input, output):
    # input[0] is the hidden states (includes batch size)
    # Shape of input[0]: (batch_size, seq_length, hidden_size)
    # Q, K, and V are computed inside the BertSelfAttention and are not directly accessible here.
    # We will infer their sizes based on the known structure.
    batch_size, seq_length, hidden_size = input[0].shape
    num_heads = module.num_attention_heads
    head_dim = hidden_size // num_heads

    # Print the sizes of the matrices involved in the dot products Q * K^T
    print(f"Batch size: {batch_size}")
    print(f"Sequence length: {seq_length}")
    print(f"Number of heads: {num_heads}")
    print(f"Head dimension: {head_dim}")
    print(f"Dot product operation between Q and K^T involves matrices of size ({batch_size}, {num_heads}, {seq_length}, {head_dim}) and ({batch_size}, {num_heads}, {head_dim}, {seq_length})")

def register_attention_hooks(model):
    # Register a hook on the BertSelfAttention layer
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.modules.container.ModuleList):
            # BertModel uses ModuleList to hold layers; we target BertSelfAttention in each layer
            for layer in module:
                if hasattr(layer, 'attention'):
                    # The self-attention submodule within each BertLayer
                    self_attention_module = layer.attention.self
                    self_attention_module.register_forward_hook(attention_hook)


def print_matrix_sizes(module, input, output):
    # This function will print the size of the input matrices to each layer
    print(f"Layer: {module.__class__.__name__}")
    for i, inp in enumerate(input):
        if torch.is_tensor(inp):
            print(f"Input {i}: {inp.shape}")
    if torch.is_tensor(output):
        print(f"Output: {output.shape}")
    print()


def add_hooks(model):
    # Add hooks to each layer
    for name, layer in model.named_modules():
        if isinstance(layer, torch.nn.Linear):  # Hooks are added to Linear layers which perform matrix multiplications
            layer.register_forward_hook(print_matrix_sizes)


def main(model_name):
    # Load model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    # Add hooks to log matrix sizes
    add_hooks(model)
    register_attention_hooks(model)

    # Encode some input text and run the model
    inputs = tokenizer("Hello, world!", return_tensors="pt")
    with torch.no_grad():
        output = model(**inputs)


if __name__ == "__main__":
    model_name = "google-bert/bert-base-uncased"  # Example model
    # model_name = "EleutherAI/gpt-j-6b"
    main(model_name)
