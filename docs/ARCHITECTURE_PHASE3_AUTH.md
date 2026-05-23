# Grace Young Phase 3 - Authentication and Role-Based Access

Phase 3 adds customer/admin login and protects the admin catalog APIs with JWT bearer tokens.

## Roles

| Role | Purpose | Access |
|---|---|---|
| customer | General shopping customer | `/api/v1/auth/me`, public catalog, future cart/orders |
| admin | Operator account | Admin catalog CRUD, image upload, future orders/reels management |
| super_admin | Future owner/admin role | Same as admin plus future settings/user management |

## Seeded Local Accounts

After running `python scripts/seed_phase2_catalog.py --reset`, the script creates:

| Account | Password | Role |
|---|---|---|
| admin@graceyoung.local | Admin123! | admin |
| customer@graceyoung.local | Customer123! | customer |

## Backend Endpoints

| Endpoint | Method | Access |
|---|---|---|
| `/api/v1/auth/register` | POST | Public; creates customer |
| `/api/v1/auth/login` | POST | Public; returns JWT |
| `/api/v1/auth/me` | GET | JWT required |
| `/api/v1/admin/catalog/*` | ALL | Admin JWT required |

## Frontend Pages

| App | Page | URL |
|---|---|---|
| Client | Customer login | `http://localhost:3000/login` |
| Client | Customer registration | `http://localhost:3000/register` |
| Client | Customer account | `http://localhost:3000/account` |
| Admin | Admin login | `http://localhost:3001/login` |
| Admin | Admin dashboard | `http://localhost:3001` |
| Admin | Products | `http://localhost:3001/products` |

## Security Notes

- `JWT_SECRET_KEY` in `.env.example` is for local development only.
- Production must use a long random secret stored in a secret manager.
- Admin APIs reject customer tokens with HTTP 403.
- Tokens are stored in `localStorage` for MVP convenience. Production can move to secure HTTP-only cookies.
