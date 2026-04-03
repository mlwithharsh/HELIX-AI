from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from pathlib import Path
from typing import AsyncIterator

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from helix_backend.Core_Brain.nlp_engine.nlp_engine import NLPEngine

from ..config import Settings
from ..schemas import PersonalityProfile
from .cache import ResponseCache
from .prompt_builder import build_conditioned_prompt

logger = logging.getLogger(__name__)


class AdaptiveInferenceService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(settings.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(settings.model_name)
        self.model.to(self.device)
        self.model.eval()
        self.cache = ResponseCache(settings.cache_ttl_seconds)
        self.active_version = settings.active_model_version
        self.reload_lock = asyncio.Lock()
        # Pass API key directly from settings — no scattered os.getenv()
        self.groq_engine = NLPEngine(
            model_name=settings.groq_model_name,
            api_key=settings.groq_api_key,
        )
        logger.info(
            f"AdaptiveInferenceService initialized: model={settings.model_name}, "
            f"groq_model={settings.groq_model_name}, "
            f"groq_key={'set' if settings.groq_api_key else 'MISSING'}, "
            f"device={self.device}"
        )

    def _cache_key(self, user_id: str, message: str, profile: PersonalityProfile, personality: str) -> str:
        payload = json.dumps(
            {"user_id": user_id, "message": message, "profile": profile.model_dump(),
             "version": self.active_version, "personality": personality},
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    async def reload_adapter(self, adapter_path: str | None, model_version: str) -> None:
        async with self.reload_lock:
            self.active_version = model_version
            if adapter_path and Path(adapter_path).exists():
                self.active_version = model_version

    def choose_ab_bucket(self, versions: list[dict]) -> tuple[str, str]:
        active = [item for item in versions if item.get("status", "active") == "active"]
        if len(active) >= 2:
            chosen = active[hash(self.active_version) % len(active)]
            return chosen.get("version", self.active_version), chosen.get("ab_bucket", "A")
        return self.active_version, "A"

    def _format_messages(self, prompt: str, message: str, history: list[dict[str, str]]) -> list[dict[str, str]]:
        """Format the conversation as a clean messages array for the Groq API."""
        messages = [{"role": "system", "content": prompt}]
        for item in history[-6:]:
            role = item.get("role", "user")
            content = item.get("content", "")
            if role in {"user", "assistant"} and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": message})
        return messages

    def generate_response(
        self,
        prompt: str,
        message: str,
        history: list[dict[str, str]],
        temperature: float = 0.8,
        top_p: float = 0.92,
        max_new_tokens: int = 150,
    ) -> tuple[str, str]:
        """Generate response via Groq (primary) or local model (fallback).
        
        Returns (response_text, backend_used).
        """
        messages = self._format_messages(prompt, message, history)

        # Primary: Groq API
        logger.info(f"[Generate] Attempting Groq API with {len(messages)} messages")
        groq_response = self.groq_engine.call_groq_model(
            messages, max_tokens=max_new_tokens, temperature=temperature
        )
        if groq_response and not groq_response.startswith("[Groq Error]"):
            logger.info(f"[Generate] Groq success ({len(groq_response)} chars)")
            return groq_response, "groq"

        # Fallback: local distilgpt2
        logger.warning(f"[Generate] Groq failed: {groq_response[:80]}. Falling back to local model.")
        try:
            # Build a simple prompt for the local model
            local_prompt = f"{prompt}\nUser: {message}\nAssistant:"
            encoded = self.tokenizer(local_prompt, return_tensors="pt", truncation=True, max_length=512).to(self.device)
            generated = self.model.generate(
                **encoded,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                pad_token_id=self.tokenizer.eos_token_id,
            )
            response = self.tokenizer.decode(
                generated[0][encoded["input_ids"].shape[1]:], skip_special_tokens=True
            ).strip()
            if response:
                logger.info(f"[Generate] Local model success ({len(response)} chars)")
                return response, "local"
        except Exception as e:
            logger.error(f"[Generate] Local model error: {e}")

        return "I understand. Let me help with that.", "fallback"

    async def stream_response(
        self,
        user_id: str,
        message: str,
        profile: PersonalityProfile,
        history: list[dict[str, str]],
        retrieved_examples: list[str],
        versions: list[dict],
        personality: str,
    ) -> tuple[str, dict, AsyncIterator[str]]:
        model_version, ab_bucket = self.choose_ab_bucket(versions)
        prompt = build_conditioned_prompt(
            message, profile, history, retrieved_examples, model_version, personality
        )
        key = self._cache_key(user_id, message, profile, personality)
        cached = self.cache.get(key)

        if cached:
            response = cached
            generation_backend = "cache"
        else:
            response, generation_backend = self.generate_response(prompt, message, history)
            self.cache.set(key, response)

        async def iterator() -> AsyncIterator[str]:
            for token in response.split():
                yield json.dumps({"type": "delta", "content": token + " "}) + "\n"
                await asyncio.sleep(0.01)

        metadata = {
            "model_version": model_version,
            "personality": personality,
            "generation_backend": generation_backend,
        }
        return response, metadata, iterator()
