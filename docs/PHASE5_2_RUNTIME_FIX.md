# Phase 5.2 Runtime Fix

Fixes:

1. Login endpoint accepts both JSON and form payloads.
2. Client login safely renders FastAPI validation details instead of crashing React.
3. Product images can be served through `https://api.kgraceyoung.com/api/v1/assets/...` to avoid HTTPS mixed-content blocks.

After deployment, rebuild backend and client, then reseed products so DB image URLs use the HTTPS asset endpoint.
