---
document_id: rb-dependency-timeouts
title: Inventory dependency timeout runbook (synthetic)
service: order-api
document_type: runbook
revision: '2026-10-18'
---
# Synthetic dependency runbook

## Distinguishing checks
DEPENDENCY_REQUEST_TIMEOUT means the order-api inventory client exceeded its 1500 ms request deadline. Inspect dependency_name, upstream_status, inventory_request_ms and trace spans for the same request_id and time window. A missing upstream_status can mean no response was received before the deadline; it does not establish whether inventory-api completed the operation. Compare database pool metrics separately: DB_POOL_ACQUIRE_TIMEOUT indicates waiting for a database slot, not an inventory response.

## Follow-up evidence
Compare caller timeout counts with inventory-api latency, error rates and request volume. Inspect whether time was spent connecting or waiting for a response, and check recent dependency changes. A timeout could reflect network delay, upstream overload or an overly tight deadline. Without traces and dependency-side evidence, do not claim one of these as the actual cause.

## Retry boundary
Do not blindly retry the stock-reservation POST. The client has no automatic retry: an earlier request may have reserved stock despite the caller timing out. Confirm the operation outcome and the service's idempotency contract before considering a retry. This corpus does not define a universal retry count or authorize an execution step.
