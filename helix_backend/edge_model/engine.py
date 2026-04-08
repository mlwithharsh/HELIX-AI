import os
import logging
import time
import psutil
import subprocess
import requests
import json
import threading
from typing import List, Dict, Optional, Generator

class EdgeEngine:
    """Production Edge Engine using llama-server.exe sidecar for robustness."""
    def __init__(self, model_path: str = None):
        self.logger = logging.getLogger("HELIX.EdgeEngine")
        
        # Paths
        self.edge_dir = os.path.dirname(os.path.abspath(__file__))
        # OS-Aware binary selection
        binary_name = "llama-server.exe" if os.name == "nt" else "llama-server"
        self.server_bin = os.path.join(self.edge_dir, binary_name)
        
        # Project base (one level up from edge_model/)
        _base = os.path.dirname(self.edge_dir)
        # Multi-Path Lookup for Render compatibility
        search_paths = [
            os.path.join(_base, "models", "qwen2-05b-v1.gguf"),
            os.path.join(_base, "helix_backend", "models", "qwen2-05b-v1.gguf"),
            os.path.join(os.path.dirname(_base), "models", "qwen2-05b-v1.gguf"),
            os.path.join(os.getcwd(), "models", "qwen2-05b-v1.gguf"),
            os.path.join(os.getcwd(), "helix_backend", "models", "qwen2-05b-v1.gguf"),
        ]
        found_model = None
        for p in search_paths:
            if os.path.exists(p):
                found_model = p
                self.logger.info(f"Lifecycle: Model found at {p}")
                break
        
        self.model_path = model_path or os.getenv("LOCAL_MODEL_PATH", found_model or search_paths[0])

        
        # State
        self.process: Optional[subprocess.Popen] = None
        self.port = 8081 # Use 8081 for internal sidecar
        self.is_loaded = False
        self.is_downloading = False
        self.last_used = 0
        self.idle_timeout = int(os.getenv("HELIX_EDGE_IDLE_TIMEOUT_SECONDS", "1800"))
        self._lock = threading.Lock()
        self._idle_thread_started = False

    def _ensure_model_exists(self) -> bool:
        """Self-healing: Download model if missing on Render."""
        if os.path.exists(self.model_path):
            return True
            
        with self._lock:
            if self.is_downloading:
                return False # Still in progress
            
            self.is_downloading = True
            self.logger.info(f"Lifecycle: Model missing! Starting self-healing download to {self.model_path}")
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            url = "https://huggingface.co/Qwen/Qwen2-0.5B-Instruct-GGUF/resolve/main/qwen2-0_5b-instruct-q4_0.gguf"
            try:
                import requests
                with requests.get(url, stream=True, timeout=30) as r:
                    r.raise_for_status()
                    with open(self.model_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                self.logger.info("Lifecycle: Model download successful.")
                self.is_downloading = False
                return True
            except Exception as e:
                self.logger.error(f"Lifecycle: Model download failed. {e}")
                self.is_downloading = False
                return False

        return False

    def _idle_monitor(self):
        while True:
            time.sleep(30)
            if self.is_loaded and (time.time() - self.last_used > self.idle_timeout):
                with self._lock:
                    self.logger.info("Lifecycle: Idle timeout. Unloading sidecar...")
                    self.unload_model()

    def unload_model(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            self.process = None
        self.is_loaded = False
        self.logger.info("Lifecycle: llama-server sidecar terminated.")

    def warmup(self) -> bool:
        with self._lock:
            return self.load_model()

    def load_model(self) -> bool:
        if self.is_loaded and self.process and self.process.poll() is None:
            self.last_used = time.time()
            return True

        # Render Free Tier Guard: Abort if RAM is critically low
        available_ram_mb = psutil.virtual_memory().available / (1024 * 1024)
        if available_ram_mb < 128:
            self.logger.error(f"Lifecycle: OOM risk! Only {available_ram_mb:.0f}MB RAM free. Aborting edge start.")
            return False

        # Self-healing check
        if not self._ensure_model_exists():
             self.logger.error("Lifecycle: Model still missing after self-healing attempt.")
             return False

        if not os.path.exists(self.server_bin):
            self.logger.error(f"Binary missing: {self.server_bin}")
            return False


        try:
            self.logger.info(f"Lifecycle: Starting llama-server sidecar on port {self.port}...")
            # Optimized for CPU usage on 8GB machines
            cmd = [
                self.server_bin,
                "--model", self.model_path,
                "--port", str(self.port),
                "--ctx-size", "2048",
                "--threads", str(min(4, os.cpu_count() or 4)),
                "--parallel", "1",
                "--n-gpu-layers", "0" # CPU Only
            ]
            
            # Start process quietly
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=self.edge_dir
            )
            
            # Wait for server to be ready
            max_wait = 30
            for i in range(max_wait):
                try:
                    res = requests.get(f"http://localhost:{self.port}/health", timeout=1)
                    if res.status_code == 200:
                        self.is_loaded = True
                        self.last_used = time.time()
                        if not self._idle_thread_started:
                            threading.Thread(target=self._idle_monitor, daemon=True).start()
                            self._idle_thread_started = True
                        self.logger.info("Lifecycle: Sidecar READY.")
                        return True
                except:
                    pass
                time.sleep(1)
            
            self.logger.error("Lifecycle: Sidecar failed to start within timeout.")
            return False
        except Exception as e:
            self.logger.error(f"Lifecycle: Startup failure. {e}")
            return False

    def generate_stream(self, messages: List[Dict[str, str]], max_tokens: int = 512, timeout: int = 15) -> Generator[str, None, None]:
        if not self.load_model():
            self.logger.warning("EdgeEngine: Sidecar failed. No fallback tokens yielded.")
            return # DON'T yield an error string, so NLPEngine can fallback

        try:
            self.last_used = time.time()
            prompt = self._format_prompt(messages)
            
            # Call llama-server OAI compatible endpoint
            payload = {
                "prompt": prompt,
                "n_predict": max_tokens,
                "stream": True,
                "stop": ["<|im_start|>", "<|im_end|>", "</s>"]
            }
            
            response = requests.post(
                f"http://localhost:{self.port}/completion",
                json=payload,
                stream=True,
                timeout=timeout
            )
            
            for line in response.iter_lines():
                if line:
                    chunk = line.decode('utf-8')
                    if chunk.startswith("data: "):
                        data = json.loads(chunk[6:])
                        token = data.get("content", "")
                        if token:
                            yield token
            
            self.last_used = time.time()
        except Exception as e:
            self.logger.error(f"Edge Streaming Error: {e}")
            yield f"\n[Edge Error]: {e}"

    def generate(self, messages: List[Dict[str, str]], max_tokens: int = 512, timeout: int = 15) -> str:
        full = ""
        for t in self.generate_stream(messages, max_tokens, timeout):
            full += t
        return full

    def _format_prompt(self, messages: List[Dict[str, str]]) -> str:
        formatted = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                formatted += f"<|im_start|>system\n{content}<|im_end|>\n"
            elif role == "user":
                formatted += f"<|im_start|>user\n{content}<|im_end|>\n"
            elif role == "assistant":
                formatted += f"<|im_start|>assistant\n{content}<|im_end|>\n"
        formatted += "<|im_start|>assistant\n"
        return formatted

# Singleton
edge_engine = EdgeEngine()
