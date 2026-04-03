# Full-Stack Adaptive Conversational System

## Backend

Install:

```powershell
Set-Location -LiteralPath 'D:\ECHO V1'
.venv\Scripts\activate
python -m pip install -r echo_backend\requirements_fullstack.txt
```

Run FastAPI:

```powershell
uvicorn echo_backend.fullstack.main:app --reload --port 8000
```

Environment variables:

```powershell
$env:ECHO_API_TOKEN='dev-token'
$env:SUPABASE_URL='https://<project>.supabase.co'
$env:SUPABASE_SERVICE_ROLE_KEY='<service-role-key>'
$env:ECHO_MODEL_NAME='distilgpt2'
$env:ECHO_MODEL_VERSION='baseline-distilgpt2'
```

## Supabase

Apply schema from:

`supabase/schema.sql`

Required tables:

- `users`
- `interactions`
- `feedback`
- `embeddings`
- `model_versions`

## Frontend

Run:

```powershell
Set-Location -LiteralPath 'D:\ECHO V1\echo-v1-frontend'
$env:VITE_BACKEND_URL='http://localhost:8000'
$env:VITE_API_TOKEN='dev-token'
npm run dev
```

## Offline RLHF job

Run batch retraining:

```powershell
Set-Location -LiteralPath 'D:\ECHO V1'
.venv\Scripts\python -m echo_backend.fullstack.offline_rlhf --batch-limit 100 --version-label candidate
```

## Primary endpoints

- `GET /api/status`
- `GET /api/users/{user_id}/profile`
- `PUT /api/users/{user_id}/profile`
- `GET /api/users/{user_id}/history`
- `POST /api/chat`
- `POST /api/chat/stream`
- `POST /api/feedback`
- `POST /api/training/run`
- `GET /api/model/versions`
