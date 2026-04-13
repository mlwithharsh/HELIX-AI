# Project Structure and Architecture

HELIX AI is designed with a modular architecture to allow for independent scaling of the edge engine, cloud orchestrator, and autonomous agents.

## Architectural Layers

### 1. Input/Interface Layer (`helix-frontend`)
- **React-Vite Core**: A high-speed frontend using modern React patterns.
- **SSE Consumer**: Handles real-time server-sent events for streaming AI responses.
- **Client API Wrapper**: A centralized service for all backend communication, ensuring consistent error handling and authentication.
- **Adaptive UI**: Dynamic interface elements that react to model latency and routing decisions.

### 2. Processing & Orchestration Layer (`helix_backend`)
- **FastAPI Core**: The primary asynchronous engine managing routing, authentication, and state.
- **Adaptive Router**: Analyzes complexity and network health to decide between Edge and Cloud execution.
- **Cognitive Brain (`Core_Brain`)**:
    - **NLP Engine**: Handles intent classification and input sanitization.
    - **Personality Router**: Managed specialized AI identities (Suzi, Helix).
    - **Memory Manager**: Manages short-term and long-term context state.
- **Autonomous Agents (`fullstack/marketing`)**: Domain-specific intelligence layers for task automation.

### 3. Execution & Data Layer
- **Edge Sidecar**: A local binary-based inference engine (llama.cpp) for offline processing.
- **Repository Pattern**: Abstracted database access layer supporting both Cloud (Supabase) and Local (SQLite/JSON) storage.
- **RLHF Engine**: A dedicated pipeline for Reinforcement Learning from Human Feedback.

## System Design
The system is strictly decoupled. The UI does not know *how* a response is generated; it only knows the data format. This allows us to swap a local model for a remote API without modifying a single line of frontend code.

## Future Scalability Plan
- **Distributed Agents**: Moving from local schedulers to distributed task queues (Celery/RabbitMQ).
- **Vectorized RAG**: Integration of ChromaDB or FAISS for million-token long-term memory.
- **Hardware Abstraction**: Expanding the Edge Sidecar to support Metal (Mac), CUDA (NVIDIA), and Vulkan (Generic) acceleration.
- **Multimodal Ingestion**: Adding dedicated pipelines for image perception and real-time audio analysis.
