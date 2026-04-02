from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

import torch
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer


@dataclass
class ModelConfig:
    model_name: str = "distilgpt2"
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    max_length: int = 256
    trust_remote_code: bool = False


def get_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def build_lora_config() -> LoraConfig:
    return LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        bias="none",
        target_modules=["c_attn", "c_proj"],
    )


def load_model_and_tokenizer(config: ModelConfig) -> Tuple[Any, Any, Dict[str, Any]]:
    device = get_device()
    tokenizer = AutoTokenizer.from_pretrained(
        config.model_name,
        trust_remote_code=config.trust_remote_code,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dtype = torch.float16 if device == "cuda" else torch.float32
    base_model = AutoModelForCausalLM.from_pretrained(
        config.model_name,
        torch_dtype=dtype,
        trust_remote_code=config.trust_remote_code,
    )

    peft_model = get_peft_model(base_model, build_lora_config())
    peft_model.to(device)

    metadata = {
        "device": device,
        "dtype": str(dtype),
        "model_name": config.model_name,
        "peft": "lora",
    }
    return peft_model, tokenizer, metadata
