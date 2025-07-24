from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import torch

try:
    # Set up quantization to reduce memory usage
    quantization_config = BitsAndBytesConfig(
        load_in_8bit=True, bnb_8bit_compute_dtype=torch.float16
    )

    # Load tokenizer
    base_model = "meta-llama/Meta-Llama-3-8B"
    tokenizer = AutoTokenizer.from_pretrained(base_model)

    # Load base model with quantization
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=quantization_config,
        device_map="cpu",  # Force CPU to avoid CUDA issues
    )

    # Apply LoRA adapters
    lora_model = "FinGPT/fingpt-mt_llama3-8b_lora"
    model = PeftModel.from_pretrained(model, lora_model)

    print("Model loaded successfully!")
except Exception as e:
    print(f"Model loading failed: {e}")
