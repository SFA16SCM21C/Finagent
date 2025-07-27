from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from accelerate import init_empty_weights, load_checkpoint_and_dispatch
import torch
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

try:
    # Load tokenizer with authentication
    token = os.getenv("HF_TOKEN")
    if not token:
        raise ValueError("HF_TOKEN not found in .env file. Please set it.")
    base_model = "meta-llama/Llama-2-7b-hf"
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
        dtype=torch.float16,
        token=token
    )

    # Apply LoRA adapters
    model = PeftModel.from_pretrained(model, "FinGPT/fingpt-mt_llama3-8b_lora", token=token)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Model loading failed: {e}")