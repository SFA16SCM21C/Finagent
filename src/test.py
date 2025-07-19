from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

# Load base model and tokenizer
base_model = "meta-llama/Meta-Llama-3-8B"
tokenizer = AutoTokenizer.from_pretrained(base_model)
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(
    base_model, torch_dtype=torch.float16, device_map="auto"
)

# Apply LoRA adapters
lora_model = "FinGPT/fingpt-mt_llama3-8b_lora"
model = PeftModel.from_pretrained(model, lora_model)

# Test inference
prompt = "What is the capital of France?"
inputs = tokenizer(prompt, return_tensors="pt").to(
    "cuda" if torch.cuda.is_available() else "cpu"
)

# Testing output
outputs = model.generate(**inputs, max_length=50)

# Print output
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
