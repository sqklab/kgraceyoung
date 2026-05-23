# Grace Young Phase 5 — Cart, Wishlist, Address Book, Order Creation, Docker Production

## Scope

Phase 5 adds the first end-to-end customer commerce workflow:

1. Customer authentication from Phase 3
2. Cart API and customer cart page
3. Wishlist API and customer wishlist page
4. Customer address book API and checkout address form
5. Order creation from cart
6. Admin order review page
7. Production Dockerfiles for backend, client, and admin
8. `docker-compose.prod.yml` for deploy testing

## New backend APIs

All customer commerce routes require a customer JWT token.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/commerce/cart` | Read current cart |
| POST | `/api/v1/commerce/cart/items` | Add product to cart |
| PATCH | `/api/v1/commerce/cart/items/{item_id}` | Change quantity; `0` removes item |
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
| GET | `/api/v1/admin/orders` | Admin order monitor |

## Order model

Orders are created as `pending_payment`, `unpaid`, and `unfulfilled`. Payment capture, Stripe/PayPal webhook, shipping label creation, and inventory deduction should be added in later phases.

## Docker production ports

| Service | Host port | Container port |
|---|---:|---:|
| Client | `13000` | `3000` |
| Admin | `13001` | `3001` |
| Backend API | `18000` | `8000` |
| MinIO API | `19000` | `9000` |
| MinIO Console | `19001` | `9001` |
| Meilisearch | `17700` | `7700` |

## Recommended Nginx Proxy Manager hosts

| Domain | Forward target |
|---|---|
| `kgraceyoung.com`, `www.kgraceyoung.com` | `http://172.17.0.1:13000` |
| `admin.kgraceyoung.com` | `http://172.17.0.1:13001` |
| `api.kgraceyoung.com` | `http://172.17.0.1:18000` |

Keep HTTP/2 off if your current NPM image/nginx build rejects the generated `http2` directive.

## Deploy test

```bash
cp .env.prod.example .env
# Edit passwords and public origins first.
docker compose -f docker-compose.prod.yml --env-file .env build
docker compose -f docker-compose.prod.yml --env-file .env up -d
```

Run sample catalog seed after the backend is healthy:

```bash
docker compose -f docker-compose.prod.yml --env-file .env exec backend python scripts/seed_phase2_catalog.py --reset
```

Default users after seed:

| Type | Email | Password |
|---|---|---|
| Admin | `admin@graceyoung.local` | `Admin123!` |
| Customer | `customer@graceyoung.local` | `Customer123!` |

## Manual checkout smoke test

1. Open client.
2. Log in as `customer@graceyoung.local`.
3. Add a product to cart.
4. Open `/cart` and confirm item count/subtotal.
5. Open `/checkout`, save address, create order.
6. Open admin `/orders` and confirm the order appears.
