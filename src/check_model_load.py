from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

try:
    # Load tokenizer
    base_model = "meta-llama/Meta-Llama-3-8B"
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    tokenizer.pad_token = tokenizer.eos_token

    # Load base model on CPU with disk offload
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.float16,  # Lower precision
        device_map="cpu",  # Force CPU
        offload_folder="offload",
        offload_state_dict=True,
    )

    # Apply LoRA adapters
    lora_model = "FinGPT/fingpt-mt_llama3-8b_lora"
    model = PeftModel.from_pretrained(model, lora_model)

    print("Model loaded successfully!")
except Exception as e:
    print(f"Model loading failed: {e}")
