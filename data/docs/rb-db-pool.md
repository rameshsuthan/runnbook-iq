---
document_id: rb-db-pool
title: Database connection-pool exhaustion runbook (synthetic)
service: order-api
document_type: runbook
revision: '2026-10-18'
---
# Synthetic database runbook

## Distinguishing checks
DB_POOL_ACQUIRE_TIMEOUT means order-api waited 500 ms for a pool slot. Compare db_pool_in_use with the per-process limit of 20, db_pool_waiters, and db_pool_acquire_ms for the same process and time window. A full pool with waiting requests supports investigating pool contention; it does not prove that PostgreSQL itself is unavailable. The error differs from DEPENDENCY_REQUEST_TIMEOUT, which describes waiting for inventory-api rather than acquiring a database connection.

## Follow-up evidence
Inspect active and long-running transaction durations, connection checkout duration and recent request concurrency. Correlate slow inventory calls with long checkouts to test whether a code path holds a connection while waiting on a dependency. The intended request path calls inventory-api before acquiring a database connection. A connection leak, long transaction, or burst of concurrency can produce similar symptoms; request traces and pool metrics are needed to distinguish them.

## Safe interpretation
Do not increase the pool size or restart services solely from the error code. Gather the affected process IDs, interval, pool metrics, transaction durations and recent code/configuration changes. A historical incident is an example, not proof of the current cause. This assistant cannot inspect these signals or perform remediation.
