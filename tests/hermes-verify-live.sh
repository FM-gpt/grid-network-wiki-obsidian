#!/bin/bash
# Comprehensive live environment test for GRID Wiki on CT131
set -e

HOST="10.10.30.131"
PORT="8082"
BASE="http://${HOST}:${PORT}"
PASS=0
FAIL=0

echo "=== COMPREHENSIVE LIVE ENVIRONMENT TEST ==="
echo "Testing GRID Wiki on ${BASE}"
echo ""

# Test 1: Root Dashboard
echo "--- Test 1: Root Dashboard ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/" 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
    echo "✅ PASS: Root returns HTTP 200"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL: Root returns HTTP $CODE (expected 200)"
    FAIL=$((FAIL + 1))
fi

# Test 2: Dashboard Status API
echo "--- Test 2: Dashboard Status API ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/api/dashboard/status" 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
    echo "✅ PASS: Dashboard status API returns HTTP 200"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL: Dashboard status API returns HTTP $CODE (expected 200)"
    FAIL=$((FAIL + 1))
fi

# Test 3: Wiki Index API
echo "--- Test 3: Wiki Index API ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/api/wiki-index" 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
    echo "✅ PASS: Wiki index API returns HTTP 200"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL: Wiki index API returns HTTP $CODE (expected 200)"
    FAIL=$((FAIL + 1))
fi

# Test 4: Agent Query API
echo "--- Test 4: Agent Query API ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/api/agent/query?q=grid" 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
    echo "✅ PASS: Agent query API returns HTTP 200"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL: Agent query API returns HTTP $CODE (expected 200)"
    FAIL=$((FAIL + 1))
fi

# Test 5: Monitoring Status API
echo "--- Test 5: Monitoring Status API ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/api/monitoring-status" 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
    echo "✅ PASS: Monitoring status API returns HTTP 200"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL: Monitoring status API returns HTTP $CODE (expected 200)"
    FAIL=$((FAIL + 1))
fi

# Test 6: Kanban Cards API
echo "--- Test 6: Kanban Cards API ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/api/kanban/all" 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
    echo "✅ PASS: Kanban cards API returns HTTP 200"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL: Kanban cards API returns HTTP $CODE (expected 200)"
    FAIL=$((FAIL + 1))
fi

# Test 7: Active Tasks API
echo "--- Test 7: Active Tasks API ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/api/active-tasks" 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
    echo "✅ PASS: Active tasks API returns HTTP 200"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL: Active tasks API returns HTTP $CODE (expected 200)"
    FAIL=$((FAIL + 1))
fi

# Test 8: Project Manifest API
echo "--- Test 8: Project Manifest API ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/api/project-manifest" 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
    echo "✅ PASS: Project manifest API returns HTTP 200"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL: Project manifest API returns HTTP $CODE (expected 200)"
    FAIL=$((FAIL + 1))
fi

# Test 9: Sites API
echo "--- Test 9: Sites API ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/api/sites" 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
    echo "✅ PASS: Sites API returns HTTP 200"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL: Sites API returns HTTP $CODE (expected 200)"
    FAIL=$((FAIL + 1))
fi

# Test 10: Drift Reports API
echo "--- Test 10: Drift Reports API ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/api/drift-reports" 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
    echo "✅ PASS: Drift reports API returns HTTP 200"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL: Drift reports API returns HTTP $CODE (expected 200)"
    FAIL=$((FAIL + 1))
fi

# Test 11: Export API
echo "--- Test 11: Export API ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/api/export" 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
    echo "✅ PASS: Export API returns HTTP 200"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL: Export API returns HTTP $CODE (expected 200)"
    FAIL=$((FAIL + 1))
fi

# Test 12: Wiki Page API
echo "--- Test 12: Wiki Page API ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/api/wiki/grid-infrastructure-overview" 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
    echo "✅ PASS: Wiki page API returns HTTP 200"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL: Wiki page API returns HTTP $CODE (expected 200)"
    FAIL=$((FAIL + 1))
fi

# Test 13: Settings API
echo "--- Test 13: Settings API ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/api/settings" 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
    echo "✅ PASS: Settings API returns HTTP 200"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL: Settings API returns HTTP $CODE (expected 200)"
    FAIL=$((FAIL + 1))
fi

# Test 14: Static CSS
echo "--- Test 14: Static CSS ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/css/dashboard.css" 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
    echo "✅ PASS: CSS file returns HTTP 200"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL: CSS file returns HTTP $CODE (expected 200)"
    FAIL=$((FAIL + 1))
fi

# Test 15: Static JS
echo "--- Test 15: Static JS ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/js/dashboard.js" 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
    echo "✅ PASS: JS file returns HTTP 200"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL: JS file returns HTTP $CODE (expected 200)"
    FAIL=$((FAIL + 1))
fi

# Test 16: Static HTML
echo "--- Test 16: Static HTML ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/monitoring.html" 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
    echo "✅ PASS: Monitoring HTML returns HTTP 200"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL: Monitoring HTML returns HTTP $CODE (expected 200)"
    FAIL=$((FAIL + 1))
fi

# Test 17: Wiki Index JSON
echo "--- Test 17: Wiki Index JSON ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/dashboard/wiki-index.json" 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
    echo "✅ PASS: Wiki index JSON returns HTTP 200"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL: Wiki index JSON returns HTTP $CODE (expected 200)"
    FAIL=$((FAIL + 1))
fi

# Test 18: Agent Query with different query
echo "--- Test 18: Agent Query with different query ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/api/agent/query?q=monitoring" 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
    echo "✅ PASS: Agent query with 'monitoring' returns HTTP 200"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL: Agent query with 'monitoring' returns HTTP $CODE (expected 200)"
    FAIL=$((FAIL + 1))
fi

# Test 19: Service is running
echo "--- Test 19: Service is running ---"
if curl -s --max-time 5 "${BASE}/" > /dev/null 2>&1; then
    echo "✅ PASS: Service is responding"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL: Service is not responding"
    FAIL=$((FAIL + 1))
fi

# Test 20: Caddy proxy for wiki.grid
echo "--- Test 20: Caddy proxy for wiki.grid ---"
CODE=$(curl -sk -o /dev/null -w '%{http_code}' "https://wiki.grid.home.arpa/" 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
    echo "✅ PASS: Caddy proxy for wiki.grid returns HTTP 200"
    PASS=$((PASS + 1))
else
    echo "⚠️  INFO: Caddy proxy for wiki.grid returns HTTP $CODE (may be expected if DNS not configured)"
fi

echo ""
echo "=== RESULTS ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo "Total:  $((PASS + FAIL))"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✅ ALL TESTS PASSED"
else
    echo "❌ SOME TESTS FAILED"
fi

exit $FAIL
