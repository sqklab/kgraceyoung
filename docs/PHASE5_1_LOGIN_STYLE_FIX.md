# Phase 5.1 Login and Premium UI Fix

## What changed

- Added `bcrypt==4.0.1` to prevent passlib/bcrypt seed errors.
- Improved customer login error handling so DNS/API proxy failures are shown clearly instead of a silent console error.
- Improved admin login error handling.
- Added a more premium login layout, hover states, button transitions, focus states, and typography refinements.

## Important DNS requirement

The browser error `net::ERR_NAME_NOT_RESOLVED` for `https://api.kgraceyoung.com` means DNS is missing.

Route 53 records required:

```text
kgraceyoung.com          A    34.48.83.76
www.kgraceyoung.com      A    34.48.83.76
admin.kgraceyoung.com    A    34.48.83.76
api.kgraceyoung.com      A    34.48.83.76
```

Nginx Proxy Manager proxy hosts required:

```text
kgraceyoung.com, www.kgraceyoung.com  -> http://172.17.0.1:13000
admin.kgraceyoung.com                 -> http://172.17.0.1:13001
api.kgraceyoung.com                   -> http://172.17.0.1:18000
```

Keep HTTP/2 off if the current Nginx Proxy Manager image does not support the generated directive.

## Rebuild

```bash
docker compose -f docker-compose.prod.yml --env-file .env build --no-cache backend client admin
docker compose -f docker-compose.prod.yml --env-file .env up -d backend client admin

docker compose -f docker-compose.prod.yml --env-file .env exec backend alembic upgrade head
docker compose -f docker-compose.prod.yml --env-file .env exec backend python scripts/seed_phase2_catalog.py --reset
```
