from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch
from accelerate import dispatch_model, load_checkpoint_and_dispatch

# Load tokenizer
base_model = "meta-llama/Meta-Llama-3-8B"
tokenizer = AutoTokenizer.from_pretrained(base_model)
tokenizer.pad_token = tokenizer.eos_token

# Load base model with disk offload
model = load_checkpoint_and_dispatch(
    AutoModelForCausalLM.from_pretrained(base_model, low_cpu_mem_usage=True),
    checkpoint=base_model,
    device_map="auto",  # Still use 'auto' but with disk offload
    offload_folder="offload",  # Create a folder for offloaded weights
    offload_state_dict=True  # Enable disk offload for state dict
)

# Apply LoRA adapters
lora_model = "FinGPT/fingpt-mt_llama3-8b_lora"
model = PeftModel.from_pretrained(model, lora_model)

# Test inference
prompt = "What is the capital of France?"
inputs = tokenizer(prompt, return_tensors="pt").to("cpu")  # Use CPU if GPU is limited
outputs = model.generate(**inputs, max_length=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))