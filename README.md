## WhatTheMacro (Macro Tracker)

Minimal macro-tracking app with:
- **Frontend**: React (Vite) – upload a meal photo for macro estimation, manage targets, view intake/history.
- **Backend**: FastAPI + SQLite – endpoints for intake/targets, AI photo estimation (OpenAI), optional barcode lookup (OpenFoodFacts), and JWT-based auth.

### Architecture
- `frontend/`: Vite React app (served by Nginx in Docker)
- `backend/`: FastAPI app with SQLite DB (`backend/app.db`)
- `docker-compose.yaml`: builds and runs both services

### Prerequisites
- Option A: Docker Desktop
- Option B (local dev): Python 3.12+, Node 18+ (Node 20 recommended)

### Environment
Create `backend/.env` with:
- `OPENAI_API_KEY=...` (required for photo estimation)
- `JWT_SECRET=change-me` (set a strong secret in production)

SQLite DB file lives at `backend/app.db` (Docker maps it into the container for persistence).

### Quickstart (Docker)
1) Set `backend/.env` as above
2) Build and start
```
docker compose up -d --build
```
3) Open:
- Frontend: http://localhost:3000
- API: http://localhost:8000/api

### Local Development
Backend (FastAPI):
```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # if you have one; otherwise create .env with keys listed above
export PYTHONPATH=$PWD/src
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Frontend (React):
```
cd frontend
npm install
# Ensure API base URL matches your backend in src/config.js (e.g., http://localhost:8000/api)
npm run dev
```

### Auth & Protected Endpoints
Auth uses JWT bearer tokens.
- Signup: `POST /api/signup` with JSON `{ "email": "you@example.com", "password": "secret123" }`
- Login: `POST /api/login` with form fields `username`, `password` (content-type: `application/x-www-form-urlencoded`)
- Both return `{ access_token, token_type }`. Send `Authorization: Bearer <token>` for all routes below.

Protected routes (all application routes are protected now):
- Intake: `GET /api/intake/{date}`, `POST /api/intake` (form-data), `DELETE /api/intake/{entry_id}`
- Targets: `GET /api/targets`, `GET /api/targets/history`, `POST /api/targets`
- AI/Logs: `POST /api/estimate-macro` (multipart file `image`), `GET /api/openai-logs`

Example: signup, login, and update targets
```
# Signup
curl -X POST http://localhost:8000/api/signup \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","password":"secret123"}'

# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=test@example.com&password=secret123' | \
  python -c 'import sys, json; print(json.load(sys.stdin)["access_token"])')

# Update targets (protected)
curl -X POST http://localhost:8000/api/targets \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"protein":160,"carbs":155,"fat":60,"calories":1800}'

# Read targets (protected)
curl http://localhost:8000/api/targets \
  -H "Authorization: Bearer $TOKEN"

# Estimate macro from image (protected)
curl -X POST http://localhost:8000/api/estimate-macro \
  -H "Authorization: Bearer $TOKEN" \
  -F image=@/path/to/meal.jpg
```

### Tests (backend)
Run locally:
```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-test.txt
pytest -q
```

Or inside the backend container:
```
docker compose exec -T backend sh -lc 'pip install pytest pytest-mock httpx && python -m pytest -q'
```

### Makefile
Convenience commands at repo root:
```
# Show available targets
make help

# Build and run with Docker Compose
make compose-up      # builds and starts in background
make compose-build   # just builds images
make compose-logs    # follow logs
make compose-down    # stop and remove

# Backend tests
make test            # uses uv to create venv, install deps, run pytest
make test-docker     # run pytest inside backend container
```

Note: `make test` requires `uv`. Install with:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Configuration notes
- Frontend API URL: edit `frontend/src/config.js` → `export const API_URL = "http://localhost:8000/api"`
- Database: `backend/app.db` is persisted (and mounted in Docker)
- CORS: backend allows all origins by default (adjust in `backend/src/main.py` if needed)

### Endpoints (quick reference)
- Intake: `GET /api/intake/{date}`, `POST /api/intake` (form-data), `DELETE /api/intake/{entry_id}`
- Targets: `GET /api/targets`, `GET /api/targets/history`, `POST /api/targets`
- AI/Logs: `POST /api/estimate-macro` (multipart file `image`), `GET /api/openai-logs`

