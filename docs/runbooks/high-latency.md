# Runbook: High Latency Alerts

## Symptoms
- Latency SLO is not being met (< 95% of checks under 500ms)
- Error budget for latency is depleting
- Grafana shows p95 response time trending upward

## Severity
**Medium to High** - Depends on user impact. High latency often precedes outages.

## Immediate Actions

### 1. Identify affected monitors
```sql
-- Find monitors with high average latency (last hour)
SELECT
    m.name,
    AVG(cr.response_time_ms) as avg_latency,
    MAX(cr.response_time_ms) as max_latency,
    COUNT(*) as check_count
FROM check_results cr
JOIN monitors m ON cr.monitor_id = m.id
WHERE cr.checked_at > NOW() - INTERVAL '1 hour'
  AND cr.response_time_ms IS NOT NULL
GROUP BY m.id, m.name
HAVING AVG(cr.response_time_ms) > 500
ORDER BY avg_latency DESC;
```

### 2. Check if latency is at the target or UpDog
```bash
# Test from your local machine
time curl -o /dev/null -s -w '%{time_total}' <target-url>

# Test from UpDog container
docker exec updog-api curl -o /dev/null -s -w '%{time_total}' <target-url>
```

If latency differs significantly, the issue is network-related.

## Possible Causes

### 1. Target service degradation
The monitored service itself is slow.

**Check:**
- Review target's own monitoring/APM
- Check for recent deployments to the target
- Look for increased load on target

**Resolution:**
- This is the target's issue to fix
- Document and communicate to stakeholders
- Consider adjusting SLO if this is expected behavior

### 2. Network congestion
Network path between UpDog and target is congested.

**Check:**
```bash
# Trace the route
traceroute <target-hostname>

# Check for packet loss
mtr <target-hostname>
```

**Resolution:**
- If cloud-hosted, check cloud provider status
- Contact network team if internal network issue

### 3. DNS latency
Slow DNS resolution adding to total time.

**Check:**
```bash
time dig <target-hostname>
```

**Resolution:**
- Use faster DNS servers
- Implement DNS caching
- Consider using IP addresses for critical monitors

### 4. UpDog under load
UpDog itself may be slow processing checks.

**Check:**
- Check UpDog API latency in Prometheus: `http_request_duration_seconds`
- Check container resource usage: `docker stats`

**Resolution:**
- Scale up UpDog resources
- Reduce check frequency
- Optimize database queries

## SLO Impact Assessment

Calculate error budget impact:
```
Current latency SLI: X%
Latency SLO target: 95%
Error budget remaining: Y%

If latency continues at current rate:
- Budget will be exhausted in Z hours
- Action required before: [date/time]
```

## Escalation
If latency SLO breach is imminent (< 20% error budget remaining):
1. Notify service owners
2. Consider reducing check frequency temporarily
3. Escalate to on-call engineer

## Prevention
- Set up alerts at 50% error budget consumption
- Monitor latency trends, not just point-in-time values
- Establish latency baselines for each monitor
