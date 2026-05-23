# Grace Young Commerce - Phase 5 Commerce Workflow + Docker Production

K-Beauty video commerce starter platform inspired by Olive Young-style curation, TikTok-style discovery, and Sephora-style trust.

Phase 5 keeps the previous catalog/auth/env work and adds **customer cart, wishlist, address book, order creation, admin order review, backend/client/admin Dockerfiles, and `docker-compose.prod.yml`**.

## Included

- Local Docker infrastructure: PostgreSQL, MinIO, Redis, Meilisearch, MailHog, Adminer
- Production Docker Compose: PostgreSQL, Redis, MinIO, Meilisearch, backend, client, admin
- FastAPI backend with SQLAlchemy + Alembic
- Catalog CRUD: categories, brands, products
- MinIO product image upload
- Generated seed catalog: 5 categories, 25 brands, 250 products, 250 generated product images
- Customer login/registration/account pages
- Customer cart, wishlist, checkout, order history pages
- Customer address book API
- Pending-payment order creation from cart
- Admin login, product management, order review
- JWT authentication and role-based admin protection
- Root `.env` based configuration

## Local Development

```bash
cp .env.example .env
docker compose -f docker-compose.infra.yml --env-file .env up -d
```

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python scripts/seed_phase2_catalog.py --reset
uvicorn app.main:app --reload --port 8000
```

Client:

```bash
cd frontend/client
npm install
npm run dev
```

Admin:

```bash
cd frontend/admin
npm install
npm run dev -- --port 3001
```

## Production Docker Deploy Test

```bash
cp .env.prod.example .env
# Edit all CHANGE_ME values and public URLs first.
docker compose -f docker-compose.prod.yml --env-file .env build
docker compose -f docker-compose.prod.yml --env-file .env up -d
```

Seed the sample catalog after the backend is healthy:

```bash
docker compose -f docker-compose.prod.yml --env-file .env exec backend python scripts/seed_phase2_catalog.py --reset
```

## Production Ports

| Service | URL / Port |
|---|---|
| Client | `http://SERVER_IP:13000` |
| Admin | `http://SERVER_IP:13001` |
| FastAPI | `http://SERVER_IP:18000/docs` |
| MinIO API | `http://SERVER_IP:19000` |
| MinIO Console | `http://SERVER_IP:19001` |
| Meilisearch | `http://SERVER_IP:17700` |

## Suggested Nginx Proxy Manager Mapping

| Domain | Forward target |
|---|---|
| `kgraceyoung.com`, `www.kgraceyoung.com` | `http://172.17.0.1:13000` |
| `admin.kgraceyoung.com` | `http://172.17.0.1:13001` |
| `api.kgraceyoung.com` | `http://172.17.0.1:18000` |

For your current NPM setup, keep **HTTP/2 Support OFF** until the Nginx image issue is fully confirmed resolved.

## Default Seed Accounts

| Type | Email | Password |
|---|---|---|
| Admin | `admin@graceyoung.local` | `Admin123!` |
| Customer | `customer@graceyoung.local` | `Customer123!` |

## Customer Smoke Test

1. Open client.
2. Log in as the sample customer.
3. Add product to cart from the homepage.
4. Open `/cart`.
5. Open `/checkout`, save an address, and create order.
6. Open `/orders` to view customer order history.
7. Open admin `/orders` to verify the order.

## New Phase 5 APIs

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/commerce/cart` | Read current cart |
| POST | `/api/v1/commerce/cart/items` | Add product to cart |
| PATCH | `/api/v1/commerce/cart/items/{item_id}` | Update quantity |
| DELETE | `/api/v1/commerce/cart/items/{item_id}` | Remove item |
| GET | `/api/v1/commerce/wishlist` | Read wishlist |
| POST | `/api/v1/commerce/wishlist/{product_id}` | Save product |
| DELETE | `/api/v1/commerce/wishlist/{product_id}` | Remove product |
| GET | `/api/v1/commerce/addresses` | Read address book |
| POST | `/api/v1/commerce/addresses` | Create address |
| PATCH | `/api/v1/commerce/addresses/{address_id}` | Update address |
| DELETE | `/api/v1/commerce/addresses/{address_id}` | Delete address |
| POST | `/api/v1/commerce/checkout` | Create pending-payment order from cart |
| GET | `/api/v1/commerce/orders` | Customer order history |
| GET | `/api/v1/admin/orders` | Admin order review |

| 도메인                                      | Forward                   |
| ---------------------------------------- | ------------------------- |
| `kgraceyoung.com`, `www.kgraceyoung.com` | `http://172.17.0.1:13000` |
| `admin.kgraceyoung.com`                  | `http://172.17.0.1:13001` |
| `api.kgraceyoung.com`                    | `http://172.17.0.1:18000` |



| 서비스           | Host Port |
| ------------- | --------: |
| Client        |   `13000` |
| Admin         |   `13001` |
| Backend API   |   `18000` |
| PostgreSQL    |   `15432` |
| Redis         |   `16379` |
| MinIO API     |   `19000` |
| MinIO Console |   `19001` |
| Meilisearch   |   `17700` |
| MailHog UI    |   `18025` |
| Adminer       |   `18080` |



docker network create graceyoung-net || true

docker compose -f docker-compose.infra.yml --env-file .env up -d


docker compose -f docker-compose.prod.yml --env-file .env build
docker compose -f docker-compose.prod.yml --env-file .env up -d
docker compose -f docker-compose.prod.yml --env-file .env ps
docker compose -f docker-compose.prod.yml --env-file .env exec backend alembic upgrade head
docker compose -f docker-compose.prod.yml --env-file .env exec backend python scripts/seed_phase2_catalog.py --reset

docker compose -f docker-compose.prod.yml --env-file .env build --no-cache backend
docker compose -f docker-compose.prod.yml --env-file .env up -d backend

