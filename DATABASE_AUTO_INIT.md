# Automatic Database Initialization

## Overview

The database is now automatically initialized when the FastAPI server starts. You no longer need to manually run database initialization scripts.

## How It Works

1. **On Server Startup**: When you start the server with `python run.py` or `uvicorn app.main:app`, a startup event handler automatically:
   - Checks if the database exists
   - Creates all tables if they don't exist
   - Works for both SQLite and PostgreSQL

2. **Idempotent Operation**: The initialization is safe to run multiple times:
   - If tables already exist, nothing happens
   - If tables don't exist, they are created
   - No data is lost or overwritten

## Database Creation

### SQLite (Current Setup)
- Database file: `brandfluence.db` (in project root)
- Created automatically on first server start
- All tables are created automatically

### PostgreSQL (Future Migration)
- When you switch to PostgreSQL, tables will be created automatically on first connection
- Just update `DATABASE_URL` in `.env` file
- No manual table creation needed

## Manual Initialization (Optional)

If you need to manually initialize the database (e.g., for testing), you can still use:

```python
from app.core.database import init_db
init_db()
```

Or run:
```bash
python -c "from app.core.database import init_db; init_db()"
```

## Startup Logs

When the server starts, you'll see logs like:
```
INFO: Initializing database...
INFO: Database initialized successfully - tables created/verified
```

## Benefits

- ✅ No manual setup required
- ✅ Works like PostgreSQL (automatic table creation)
- ✅ Safe to run multiple times
- ✅ Consistent behavior across environments

