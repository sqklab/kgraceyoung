# Phase 5.3 — Auth Persistence + Commerce UI Refactor

## Scope

- Replaced the landing-first header with a commerce-first header: logo, search, account/wishlist/cart actions, category navigation, promo strip.
- Added `AuthHeader` client component that reads `gy_customer_token`, validates `/api/v1/auth/me`, and keeps the header logged-in after navigating back from account pages.
- Changed seeded demo emails from `.local` to `@kgraceyoung.com` to avoid `email-validator` rejection.
- Reworked the home page into an Olive Young-inspired commerce layout: filter sidebar, item count/view controls, sort select, product grid, badges, ratings, cart/wishlist actions, and reels commerce section.
- Did not copy Olive Young product images or exact visual assets. Product images remain generated sample images served from MinIO through the backend asset proxy.

## Build

```bash
docker compose -f docker-compose.prod.yml --env-file .env build --no-cache client backend admin
docker compose -f docker-compose.prod.yml --env-file .env up -d --force-recreate client backend admin
```

## Re-seed demo data

```bash
docker compose -f docker-compose.prod.yml --env-file .env exec backend python scripts/seed_phase2_catalog.py --reset
```

## Demo accounts

- Customer: `customer@kgraceyoung.com` / `Customer123!`
- Admin: `admin@kgraceyoung.com` / `Admin123!`
