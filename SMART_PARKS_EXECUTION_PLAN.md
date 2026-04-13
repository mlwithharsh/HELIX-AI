# Smart Parks Execution Plan

## Objective
Build the DDA Smart Parks concept as a deployable Helix product that can run in simulator mode immediately and connect to real hardware later.

## Delivery Chunks

### Chunk 1: Platform Base
- Helix route and operator workspace
- Smart Parks backend module
- Seeded pilot parks, zones, devices
- Local SQLite-backed state for free-tier compatible development

### Chunk 2: Telemetry Runtime
- Batched telemetry ingestion endpoint
- Simulation endpoint for development and demos
- Risk classification and threshold logic
- Device heartbeat and last-seen tracking

### Chunk 3: Alerting + Operations
- Alert lifecycle: open, acknowledged, resolved
- Auto work-order creation for critical issues
- Manual work-order creation and update support
- Park-level risk summaries and report overview

### Chunk 4: Hardware Readiness
- Device registration endpoint
- Hardware contract endpoint
- Threshold discovery endpoint
- Compatible with LoRaWAN/NB-IoT gateway middleware posting into Helix

### Chunk 5: Production Upgrade Path
- Move Smart Parks state from local SQLite to Supabase/Postgres
- Attach ChirpStack webhook or MQTT bridge
- Add ThingsBoard embedding or deep link dashboards
- Add role-based access, audit logs, and PDF reporting

## Free-Tier Deployment Shape
- `helix-frontend`: Vercel Hobby
- `helix_backend`: Render/Railway/Fly.io small service or local pilot server
- `app state`: local SQLite for pilot dev, then Supabase free tier
- `IoT core`: self-hosted ChirpStack + ThingsBoard CE

## Current Build Status
- Smart Parks route exists in frontend
- Live workspace is wired to backend APIs
- Backend supports parks, zones, devices, readings, alerts, work orders, simulation, thresholds, and hardware contract

## Next Build Priorities
1. Add Supabase dependency in the Python environment so full app boot verification can run.
2. Add park map and trend charts in the frontend.
3. Add CSV/PDF monthly report generation.
4. Add authenticated field-tech workflow for maintenance closure.
