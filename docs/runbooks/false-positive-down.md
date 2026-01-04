# Runbook: Monitor Showing DOWN but Target is Up

## Symptoms
- Discord alert shows monitor as DOWN
- Manual check (curl, browser) shows the target URL is responding normally
- Grafana shows the monitor as down but other monitors are fine

## Severity
**Medium** - False positive, not actual outage. But indicates monitoring reliability issue.

## Possible Causes

### 1. Network issues between UpDog and target
The target may be up but unreachable from UpDog's network location.

**Check:**
```bash
# From the UpDog server/container
curl -v <target-url>
```

**Resolution:**
- If intermittent, may be transient network issue - monitor for recurrence
- If persistent, check firewall rules, DNS resolution, or network routing

### 2. Target is rate-limiting UpDog
The target may be blocking or rate-limiting our monitoring requests.

**Check:**
- Look at error message in check results - look for 429 status codes
- Check if User-Agent is being blocked

**Resolution:**
- Contact target owner to whitelist monitoring IPs
- Reduce check frequency for this monitor
- Add custom headers if target requires them

### 3. Timeout too aggressive
The 30-second timeout may be too short for slow endpoints.

**Check:**
```bash
# Measure actual response time
time curl -o /dev/null -s -w '%{time_total}' <target-url>
```

**Resolution:**
- If response time > 30s, the endpoint is genuinely slow
- Consider increasing timeout or flagging as expected behavior

### 4. DNS resolution failure
DNS may be failing intermittently.

**Check:**
```bash
# From UpDog server/container
nslookup <target-hostname>
dig <target-hostname>
```

**Resolution:**
- Check DNS server configuration
- Consider using IP address directly (not recommended long-term)

## Escalation
If unable to resolve after 30 minutes:
1. Check if multiple monitors are affected (indicates UpDog infrastructure issue)
2. Review recent changes to UpDog or network configuration
3. Escalate to on-call engineer

## Prevention
- Implement retry logic (check 2-3 times before alerting)
- Add synthetic monitoring from multiple locations
- Set up monitoring for the monitor (meta-monitoring)
