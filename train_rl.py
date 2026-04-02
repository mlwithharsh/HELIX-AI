from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Dict, List

import torch
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from trl import AutoModelForCausalLMWithValueHead, PPOConfig, PPOTrainer

from memory import MemoryRecord, VectorMemoryStore
from model import ModelConfig, load_model_and_tokenizer
from rl.dataset import build_demo_dataset
from rl.logging_utils import build_writer, configure_logger, log_json_line
from rl.reward import RewardFunction
from rl.state import StatePreprocessor


@dataclass
class TrainingConfig:
    model_name: str = "distilgpt2"
    batch_size: int = 1
    mini_batch_size: int = 1
    epochs: int = 1
    max_prompt_length: int = 128
    max_new_tokens: int = 64
    log_dir: str = "logs"


def build_policy_and_value_models(model_name: str):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["c_attn", "c_proj"],
    )
    policy_model = AutoModelForCausalLMWithValueHead.from_pretrained(
        model_name,
        peft_config=lora_config,
    )
    ref_model = AutoModelForCausalLMWithValueHead.from_pretrained(model_name)
    return policy_model, ref_model, tokenizer


def safe_generate(text_generator, prompt: str) -> str:
    try:
        result = text_generator(prompt, max_new_tokens=64, do_sample=True, top_p=0.9, temperature=0.8)
        generated = result[0]["generated_text"]
        return generated[len(prompt) :].strip() or "I understand. Let me help with that."
    except Exception:
        return "I understand. Let me help with that."


def derive_reward_metrics(user_input: str, response_text: str, emotional_state: List[float]) -> Dict[str, float]:
    engagement_score = min(1.0, len(response_text.split()) / 24.0)
    task_success = 1.0 if any(token in response_text.lower() for token in ["plan", "step", "help", "next"]) else 0.3
    sentiment_improvement = 0.4 if emotional_state[2] > 0.5 and any(token in response_text.lower() for token in ["calm", "step", "together"]) else 0.1
    emotional_alignment = 0.8 if emotional_state[2] > 0.5 and "together" in response_text.lower() else 0.4
    return {
        "engagement_score": engagement_score,
        "sentiment_improvement": sentiment_improvement,
        "task_success": task_success,
        "emotional_alignment": emotional_alignment,
    }


def run_training(config: TrainingConfig) -> None:
    logger = configure_logger(config.log_dir)
    writer = build_writer(f"{config.log_dir}/tensorboard")

    # Base model setup for serving and compatibility checks.
    _, _, base_metadata = load_model_and_tokenizer(ModelConfig(model_name=config.model_name))
    logger.info("Base model loaded: %s", base_metadata)

    policy_model, ref_model, tokenizer = build_policy_and_value_models(config.model_name)
    ppo_config = PPOConfig(
        model_name=config.model_name,
        learning_rate=1.41e-5,
        batch_size=config.batch_size,
        mini_batch_size=config.mini_batch_size,
        optimize_device_cache=torch.cuda.is_available(),
        log_with=None,
    )
    ppo_trainer = PPOTrainer(
        config=ppo_config,
        model=policy_model,
        ref_model=ref_model,
        tokenizer=tokenizer,
    )

    text_generator = pipeline(
        "text-generation",
        model=policy_model.pretrained_model,
        tokenizer=tokenizer,
        device=0 if torch.cuda.is_available() else -1,
    )
    reward_function = RewardFunction()
    state_preprocessor = StatePreprocessor()
    memory_store = VectorMemoryStore()

    dataset = build_demo_dataset()
    step_index = 0
    for epoch in range(config.epochs):
        for sample in dataset:
            state = state_preprocessor.preprocess(
                user_input=sample.user_input,
                emotional_state_vector=sample.emotional_state_vector,
                conversation_history=sample.history,
                user_profile_features=sample.profile,
            )
            memory_hits = memory_store.search(sample.user_input, top_k=2)
            context_lines = [f"Memory: {record.text}" for record in memory_hits]
            prompt = (
                "You are a conversational assistant fine-tuned with reinforcement learning.\n"
                f"User input: {sample.user_input}\n"
                f"Emotional state: {state.emotional_state_vector}\n"
                f"User profile: {state.user_profile_features}\n"
                f"Conversation history: {state.conversation_history}\n"
                f"Retrieved context: {context_lines}\n"
                "Assistant:"
            )

            query_tensor = tokenizer.encode(prompt, return_tensors="pt").to(ppo_trainer.accelerator.device)
            response_text = safe_generate(text_generator, prompt)
            response_tensor = tokenizer.encode(response_text, return_tensors="pt").to(ppo_trainer.accelerator.device)

            reward_metrics = derive_reward_metrics(
                user_input=sample.user_input,
                response_text=response_text,
                emotional_state=state.emotional_state_vector,
            )
            reward = reward_function.compute(response_text=response_text, metrics=reward_metrics)
            rewards = [torch.tensor(reward.total, dtype=torch.float32).to(ppo_trainer.accelerator.device)]

            logger.info("state=%s", state.to_dict())
            logger.info("action=%s", response_text)
            logger.info("reward=%s", reward.to_dict())
            log_json_line(
                f"{config.log_dir}/debug.jsonl",
                {
                    "epoch": epoch,
                    "step": step_index,
                    "state": state.to_dict(),
                    "action": response_text,
                    "reward": reward.to_dict(),
                },
            )

            try:
                stats = ppo_trainer.step([query_tensor.squeeze(0)], [response_tensor.squeeze(0)], rewards)
            except Exception as error:
                logger.exception("PPO update failed at step %s: %s", step_index, error)
                stats = {"ppo/loss/total": 0.0, "ppo/error": str(error)}

            writer.add_scalar("reward/total", reward.total, step_index)
            writer.add_scalar("reward/engagement", reward.engagement_score, step_index)
            writer.add_scalar("training/loss_total", float(stats.get("ppo/loss/total", 0.0)), step_index)

            memory_store.add(
                MemoryRecord(
                    text=sample.user_input,
                    emotional_pattern=state.emotional_state_vector,
                    metadata={"response": response_text, "reward": reward.total},
                )
            )
            step_index += 1

    memory_store.save()
    writer.close()


def parse_args() -> TrainingConfig:
    parser = argparse.ArgumentParser(description="Run PPO fine-tuning for a conversational model.")
    parser.add_argument("--model-name", default="distilgpt2")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--mini-batch-size", type=int, default=1)
    parser.add_argument("--log-dir", default="logs")
    args = parser.parse_args()
    return TrainingConfig(
        model_name=args.model_name,
        epochs=args.epochs,
        batch_size=args.batch_size,
        mini_batch_size=args.mini_batch_size,
        log_dir=args.log_dir,
    )


if __name__ == "__main__":
    run_training(parse_args())
