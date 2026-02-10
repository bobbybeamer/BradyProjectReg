# Brady Deal Registration Portal (Django)

🚧 Prototype scaffold implementing a Deal Registration Portal using Django + DRF.

## Features ✅
- Custom `User` extending `AbstractUser` with roles: PARTNER, BRADY, ADMIN
- `PartnerOrganisation` model and per-partner access control
- `Deal` model with statuses, expiry, audit trail (`DealAudit`)
- DRF `DealViewSet` with filters, pagination, CSV export, and dashboard endpoints
- Signals to log status changes and send email notifications
- Management command to check for expiring/expired deals
- Simple `Notification` model for in-app alerts

## Quick start 🔧
1. Create and activate venv (Python 3.10+ recommended)
2. pip install -r requirements.txt
3. Copy `.env.example` to `.env` and configure
4. python manage.py migrate
5. python manage.py createsuperuser
6. python manage.py runserver

### Tests

Run the test suite:

```bash
python manage.py test
```

### Scheduling expiry checks

You can run the expiry check via cron or as a scheduled task. Example cron (run nightly):

```
0 2 * * * /path/to/venv/bin/python /path/to/manage.py check_deal_expiry
```

For production, prefer Celery beat or similar async scheduler for better reliability.

## Key endpoints
- `/api/deals/` - CRUD / list (DRF router)
- `/api/deals/{id}/submit/` - Partner submits
- `/api/deals/{id}/approve/` - Brady approves
- `/api/deals/export_csv/` - CSV export
- `/api/deals/partner_dashboard/` - Partner dashboard
- `/api/deals/brady_dashboard/` - Brady dashboard

## Notes & Next steps 💡
- Add async task queue (Celery) for email/notifications in production
- Add unit & integration tests for permissions, signals, and exports
- Add frontend (React/Vue) or templates; current API is frontend-agnostic
- Implement GDPR anonymization endpoints and data retention jobs

