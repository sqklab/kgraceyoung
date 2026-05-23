# Grace Young Phase 1 Architecture

```mermaid
flowchart LR
  CLIENT[Next.js Client / Mobile PWA] --> API[FastAPI Backend]
  ADMIN[Next.js Admin] --> API
  API --> PG[(PostgreSQL)]
  API --> REDIS[(Redis)]
  API --> MINIO[(MinIO S3)]
  API --> MEILI[(Meilisearch)]
  API --> MAIL[MailHog]
  API --> QUEUE[Celery/RQ Queue - Phase 2]
  QUEUE --> WORKER[Media/Order Worker - Phase 2]
  WORKER --> MINIO
```

## Phase 1 Decisions

- **Modular monolith backend:** faster MVP delivery, cleaner migration path to services later.
- **PostgreSQL + Alembic:** schema versioning from day one.
- **MinIO first:** local S3-compatible development; later swap to AWS S3/R2 via storage adapter.
- **Meilisearch first:** simple local product search; later OpenSearch if needed.
- **Redis:** cache, carts, sessions, and queue broker candidate.
- **Next.js client/admin:** shared design system later; independent deploy targets.

## Next Phase

1. Product CRUD API and Admin UI.
2. MinIO image upload adapter.
3. Seed catalog for skin concerns and K-beauty categories.
4. Queue worker for media and webhook jobs.
5. Cart/order/payment skeleton.
