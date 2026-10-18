---
document_id: guide-telemetry
title: Telemetry field guide (synthetic)
service: order-api
document_type: guide
revision: '2026-10-18'
---
# Synthetic training document

## Correlation and pool fields
request_id identifies a caller request; trace_id connects its spans. Compare signals in the same time window and process. db_pool_in_use is the number of checked-out connections in one process; compare against 20 for the current revision. db_pool_waiters counts pending acquisitions. db_pool_acquire_ms measures time spent waiting for a slot; it is not SQL execution duration.

## Dependency fields
inventory_request_ms measures elapsed client time for an inventory request. dependency_name identifies the upstream. upstream_status is the received HTTP status when available; it may be absent on a timeout. Inspect connection-establishment and response-wait spans separately. The corpus documents field meanings but includes no current field values.
