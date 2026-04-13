# HELIX AI: Hybrid Edge-Cloud Intelligence

## Project Vision
HELIX is an advanced AI orchestration platform architected to deliver persistent intelligence through a split-brain methodology. By seamlessly integrating local Edge inference with high-performance Cloud LLMs, HELIX provides a secure, low-latency, and uninterrupted cognitive layer for individual users and enterprise automation.
<img width="1912" height="976" alt="image" src="https://github.com/user-attachments/assets/2672e71d-8269-42ef-a80b-0bed7b143cd2" />

## Why This Project Matters
The AI landscape is currently bifurcated between high-latency cloud-dependent models and resource-constrained local models. HELIX resolves this tension by:
- **Ensuring Privacy**: Sensitive data processing occurs on-device (Edge) by default.
- **Guaranteeing Reliability**: Predictive routing and mid-stream fallback ensure 100% uptime even during network instability.
- **Democratizing Intelligence**: Modular AI architecture allows for rapid integration of best-in-class open-source models.
- **Autonomous Action**: Beyond simple chat, HELIX integrates agentic frameworks for real-world task automation, specifically in cross-platform marketing and system management.

## Technical Architecture
HELIX utilizes a sophisticated Adaptive Orchestrator to manage model execution across two major vectors:
- **FastAPI Core**: A high-performance asynchronous backend managing unified state, RLHF feedback loops, and cloud routing.
- **GGUF Edge Sidecar**: A local inference engine for quantized models (Llama 3, Qwen) ensuring device-level privacy and speed.

## Roadmap Phases
- **Phase 1: Foundation**: Hybrid routing, unified API, and basic persona system (Complete).
- **Phase 2: Modular Transformation**: Decoupling architecture into swappable personality, logic, and hardware modules (Current).
- **Phase 3: Cognitive Persistence**: Long-term memory integration via vector RAG and RLHF fine-tuning loops.
- **Phase 4: HELIX Vision**: Advanced multimodal reasoning, autonomous agent swarms, and distributed intelligence clusters.

## Quick Start Guide

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher
- Git

### Backend Setup
```bash
git clone https://github.com/mlwithharsh/HELIX-AI
cd HELIX-AI
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
pip install -r helix_backend/requirements_fullstack.txt
uvicorn helix_backend.fullstack.main:app --port 8000 --reload
```

### Frontend Setup
```bash
cd helix-frontend
npm install
npm run dev
```

## Contributor Onboarding
We are building a community of engineers dedicated to the future of decentralized AI. 
1. Review the [CONTRIBUTING.md](CONTRIBUTING.md) guide.
2. Explore the [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) to understand the codebase.
3. Check our [Issue Tracker](https://github.com/mlwithharsh/HELIX-AI/issues) for `good-first-issue` labels.

## Documentation
- [Project Architecture](./PROJECT_STRUCTURE.md)
- [Contributing Guide](./CONTRIBUTING.md)
- [Contributor Roles](./CONTRIBUTORS_GUIDE.md)
- [Roadmap](./ROADMAP.md)

---
Developed by the Advanced Agentic Coding Team.
