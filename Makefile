.PHONY: infra-up infra-down backend-install backend-migrate backend-seed backend-run client-install client-run admin-install admin-run check-config

infra-up:
	docker compose -f docker-compose.infra.yml --env-file .env up -d

infra-down:
	docker compose -f docker-compose.infra.yml --env-file .env down

backend-install:
	cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

backend-migrate:
	cd backend && alembic upgrade head

backend-seed:
	cd backend && alembic upgrade head && python scripts/seed_phase2_catalog.py --reset

backend-run:
	cd backend && uvicorn app.main:app --reload --port 8000

client-install:
	cd frontend/client && npm install

client-run:
	cd frontend/client && npm run dev

admin-install:
	cd frontend/admin && npm install

admin-run:
	cd frontend/admin && npm run dev -- --port 3001

check-config:
	curl http://localhost:8000/health/config
