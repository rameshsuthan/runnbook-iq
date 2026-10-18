---
document_id: ref-errors
title: Error identifier reference (synthetic)
service: order-api
document_type: reference
revision: '2026-10-18'
---
# Synthetic training document

## Error meanings
DB_POOL_ACQUIRE_TIMEOUT: waiting longer than 500 ms for an order-api PostgreSQL pool slot. DEPENDENCY_REQUEST_TIMEOUT: the order-api inventory request exceeds 1500 ms. These describe different stages; neither code proves an underlying cause. A 503 returned to the order caller is shared by multiple failures and is insufficient for diagnosis.

## Missing upstream status
An absent upstream_status means no upstream HTTP status was captured before the request ended. It does not prove the reservation failed or that inventory-api did no work. Use the request_id, trace timing and dependency-side evidence to establish the operation outcome.
