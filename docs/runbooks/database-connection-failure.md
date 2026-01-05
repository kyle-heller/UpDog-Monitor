# Runbook: Database Connection Failures

## Symptoms
- UpDog API returns 500 errors
- Health check endpoint (`/api/health`) fails
- Logs show `ConnectionRefusedError` or `Connection pool exhausted`
- No new check results being recorded

## Severity
**Critical** - UpDog is unable to function without database connectivity.

## Immediate Actions

### 1. Verify database is running
```bash
# Check container status
docker ps | grep updog-db

# Check if PostgreSQL is accepting connections
docker exec updog-db pg_isready -U postgres
```

### 2. Check database logs
```bash
docker logs updog-db --tail 100
```

Look for:
- Out of memory errors
- Disk space issues
- Too many connections
- Crash/restart messages

### 3. Test connection manually
```bash
# From API container
docker exec updog-api python -c "
import asyncio
from sqlalchemy import text
from app.core.db import engine

async def test():
    async with engine.connect() as conn:
        result = await conn.execute(text('SELECT 1'))
        print('Connection OK:', result.scalar())

asyncio.run(test())
"
```

## Possible Causes

### 1. Database container not running

**Check:**
```bash
docker ps -a | grep updog-db
```

**Resolution:**
```bash
# Restart the database
docker compose up -d db

# Wait for healthcheck to pass
docker compose ps db
```

### 2. Connection pool exhausted
Too many connections, none available.

**Check:**
```sql
-- Connect to database directly
docker exec -it updog-db psql -U postgres -d updog_dev

-- Check active connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'updog_dev';

-- See what's holding connections
SELECT pid, usename, application_name, state, query_start, query
FROM pg_stat_activity
WHERE datname = 'updog_dev'
ORDER BY query_start;
```

**Resolution:**
```sql
-- Terminate idle connections (careful!)
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'updog_dev'
  AND state = 'idle'
  AND query_start < NOW() - INTERVAL '10 minutes';
```

Then restart the API:
```bash
docker compose restart api
```

### 3. Disk space full
PostgreSQL stops accepting writes when disk is full.

**Check:**
```bash
# Check disk usage
docker exec updog-db df -h

# Check PostgreSQL data directory
docker exec updog-db du -sh /var/lib/postgresql/data
```

**Resolution:**
- Clear old check results:
```sql
DELETE FROM check_results
WHERE checked_at < NOW() - INTERVAL '90 days';
VACUUM FULL check_results;
```
- Increase disk allocation
- Set up data retention policy

### 4. Database credentials incorrect
Environment variable mismatch.

**Check:**
```bash
# Compare API config
docker exec updog-api env | grep DATABASE

# With database config
docker exec updog-db env | grep POSTGRES
```

**Resolution:**
- Fix environment variables in docker-compose.yml
- Restart services: `docker compose up -d`

### 5. Network connectivity between containers

**Check:**
```bash
# From API container, can we reach db?
docker exec updog-api ping db -c 3

# Check Docker network
docker network inspect updog-monitor_default
```

**Resolution:**
```bash
# Recreate network
docker compose down
docker compose up -d
```

## Recovery Verification

After resolving, verify:

1. Health check passes:
```bash
curl http://localhost:8000/api/health
```

2. Check results being recorded:
```bash
# Wait for next check cycle (60s), then:
docker exec updog-db psql -U postgres -d updog_dev -c \
  "SELECT COUNT(*) FROM check_results WHERE checked_at > NOW() - INTERVAL '2 minutes';"
```

3. Monitor Grafana for data resumption

## Escalation
If unable to restore database connectivity within 15 minutes:
1. Check for data corruption
2. Consider restoring from backup
3. Escalate to database administrator

## Prevention
- Set up database connection monitoring
- Configure connection pool limits appropriately
- Implement automatic disk space alerts
- Regular database backups
- Set up data retention/cleanup jobs
