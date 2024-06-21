from llama_cpp import Llama

llm = Llama(
  model_path="./llm/Phi-3-mini-4k-instruct-q4.gguf",  # path to GGUF file
  n_ctx=2048,  # The max sequence length to use - note that longer sequence lengths require much more resources
  n_threads=16, # The number of CPU threads to use, tailor to your system and the resulting performance
  n_gpu_layers=32,verbose=False # The number of layers to offload to GPU, if you have GPU acceleration available. Set
    # to 0 if no GPU acceleration is available on your system.
)

def askAI(args):
    entdesc= args[0]
    desc = "You are a character in a 2D game. "+entdesc+" Please respond in one "
    "or two sentences describing what would like to do next only. Do not justify or elaborate. "
    "You can only use one verb. You can only use one noun or two nouns. Your possible verbs are 'move' to an "
    "object you see, 'equip' or 'unequip' an object in your inventory, 'use' an object that's equipped or "
    "useable, 'patrol', or 'rest'."
    output = llm(
        f"<|user|>\n{desc}<|end|>\n<|assistant|>",
        max_tokens=128,  # Generate up to 128 tokens
        stop=["<|end|>"],
        echo=False  # Whether to echo the prompt
    )
    print(output['choices'][0]['text'])