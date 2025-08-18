from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from huggingface_hub import login
import torch
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

try:
    # Load token and log in to Hugging Face
    token = os.getenv("HF_TOKEN")
    if not token:
        raise ValueError("HF_TOKEN not found in .env file. Please set it.")
    login(token=token)

    # Set the base model to Llama-2-7b-hf
    base_model = "meta-llama/Llama-2-7b-hf"

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model, token=token)
    tokenizer.pad_token = tokenizer.eos_token

    # Load the model with device_map="auto" for automatic device placement
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.float16,
        device_map="auto",
        low_cpu_mem_usage=True,
        token=token
    )

    # Apply LoRA adapters for Llama-2-7b
    model = PeftModel.from_pretrained(model, "FinGPT/fingpt-mt_llama2-7b_lora", token=token)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Model loading failed: {e}")

# Test the model with a prompt
prompt = "Hello, how are you?"
inputs = tokenizer(prompt, return_tensors="pt")

# Move inputs to the device of the model's first parameter
first_param_device = next(model.parameters()).device
inputs = {k: v.to(first_param_device) for k, v in inputs.items()}

# Generate output
outputs = model.generate(**inputs)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))