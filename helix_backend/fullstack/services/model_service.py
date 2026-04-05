from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from pathlib import Path
from typing import AsyncIterator

from helix_backend.Core_Brain.nlp_engine.nlp_engine import NLPEngine
from helix_backend.edge_model.engine import edge_engine

from ..config import Settings
from ..schemas import PersonalityProfile
from .cache import ResponseCache
from .prompt_builder import build_conditioned_prompt

logger = logging.getLogger(__name__)


class AdaptiveInferenceService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.device = "cpu"
        self.cache = ResponseCache(settings.cache_ttl_seconds)
        self.active_version = settings.active_model_version
        self.reload_lock = asyncio.Lock()
        
        # PRODUCTION: Use the unified Hybrid NLPEngine
        self.engine = NLPEngine() 
        
        logger.info(
            f"AdaptiveInferenceService (PRODUCTION) initialized: mode=HYBRID-GGUF, "
            f"binary={edge_engine.server_bin}"
        )

    def _load_local_model(self):
        """Lazy load the model and tokenizer only if needed to save RAM on startup."""
        if not self.settings.use_local_llm:
            raise RuntimeError("Local LLM usage is disabled in settings (HELIX_USE_LOCAL_LLM=false)")
            
        if self._model is None:
            logger.info(f"[LocalModel] Loading {self.settings.model_name} into RAM (Lazy Load)...")
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            self._tokenizer = AutoTokenizer.from_pretrained(self.settings.model_name)
            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token
            self._model = AutoModelForCausalLM.from_pretrained(self.settings.model_name)
            self._model.to(self.device).eval()
            logger.info(f"[LocalModel] {self.settings.model_name} loaded successfully.")

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
        max_new_tokens: int = 512,
        personality: str = "Helix"
    ) -> tuple[str, str]:
        """PRODUCTION: Use Hybrid Engine with Adaptive Routing."""
        messages = self._format_messages(prompt, message, history)
        
        # Use our hardened smart_generate
        response = self.engine.smart_generate(
            messages,
            max_tokens=max_new_tokens,
            temperature=temperature,
            personality=personality
        )
        
        # Extract backend used (heuristically since smart_generate returns text)
        backend = "hybrid-gguf"
        return response, backend

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
        """PRODUCTION: Stream via Hybrid engine."""
        model_version, ab_bucket = self.choose_ab_bucket(versions)
        prompt = build_conditioned_prompt(
            message, profile, history, retrieved_examples, model_version, personality
        )
        
        messages = self._format_messages(prompt, message, history)
        full_response = ""

        # Use hardened streaming engine
        async def iterator() -> AsyncIterator[str]:
            nonlocal full_response
            # Bridge synchronous generator to async iterator
            for token in self.engine.smart_generate_stream(messages, personality=personality):
                full_response += token
                yield json.dumps({"type": "delta", "content": token}) + "\n"
            
            # Cache the result once done
            key = self._cache_key(user_id, message, profile, personality)
            self.cache.set(key, full_response)

        metadata = {
            "model_version": model_version,
            "personality": personality,
            "generation_backend": "hybrid-gguf-stream",
        }
        return full_response, metadata, iterator()
