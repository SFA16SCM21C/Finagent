from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from accelerate import init_empty_weights, load_checkpoint_and_dispatch
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

    # Initialize model with empty weights
    with init_empty_weights():
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            torch_dtype=torch.float16
        )

    # Load and dispatch in chunks
    model = load_checkpoint_and_dispatch(
        model,
        checkpoint=base_model,
        device_map="auto",
        offload_folder="offload",
        offload_state_dict=True,
        dtype=torch.float16
    )

    # Apply LoRA adapters for Llama-2-7b
    model = PeftModel.from_pretrained(model, "FinGPT/fingpt-mt_llama2-7b_lora", token=token)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Model loading failed: {e}")

# Test the model with a prompt
prompt = "Hello, how are you?"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))