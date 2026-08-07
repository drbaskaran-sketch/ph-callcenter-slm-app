# Production deployment

## Supported first release

This release can be deployed for authenticated enquiry management, assignment,
follow-up, SLA monitoring, dashboards, and CSV reporting. XTEND DB2 ingestion,
HIS booking, FCM, SMS, and WhatsApp remain simulation adapters; do not represent
them to users as live integrations until vendor-specific connectors are added.

## Prepare configuration

1. Copy `.env.production.template` to `.env` on the server.
2. Set a unique `SECRET_KEY` of at least 32 random characters.
3. Set a unique admin password of at least 12 characters.
4. Set matching PostgreSQL credentials in `DATABASE_URL` and `POSTGRES_*`.
5. Set `CORS_ORIGINS` to the exact HTTPS application origin.
6. Keep `SEED_DEMO_DATA=false` for real use.

Production startup fails when placeholder secrets or wildcard CORS are present.

## Deploy and verify

```bash
docker compose config -q
docker compose build --pull
docker compose up -d
docker compose ps
curl --fail http://127.0.0.1:5173/health
```

Only the frontend is published by Compose. The backend remains on the internal
Docker network and is reached through Nginx. Terminate TLS at the supplied host
Nginx/reverse proxy before exposing the application.

After first login, create named accounts and verify their role and branch/SLM
mapping. Never share the bootstrap administrator account.

## Operations required before patient use

- Configure automated encrypted PostgreSQL backups and test restoration.
- Ship application and reverse-proxy logs to restricted centralized storage.
- Add uptime monitoring for `/health` and disk/database-capacity alerts.
- Establish retention, consent, access-review, and incident-response policies.
- Perform an independent security assessment before internet exposure.
