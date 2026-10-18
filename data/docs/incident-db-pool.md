---
document_id: incident-db-pool
title: Pool checkout regression incident (synthetic)
service: order-api
document_type: incident
revision: '2026-10-18'
---
# Synthetic training document

## Timeline
Historical synthetic incident on 2026-09-04, all times UTC. At 10:00 a release introduced growing DB_POOL_ACQUIRE_TIMEOUT counts. At 10:08 traces showed a connection was checked out before an inventory-api call and held during slow inventory responses. At 10:17 operators rolled back the release. By 10:22 acquisition waits returned to the pre-incident range.

## Findings and scope
The affected revision used 12 connections per process. The confirmed finding for this historical incident was a code path holding database connections across inventory calls; it was not proof that PostgreSQL capacity was exhausted. The corrective change moved connection acquisition after the inventory operation and added a regression test. The current revision uses 20 connections after a separate capacity review; increasing the pool was not the documented incident fix. This historical finding does not diagnose a new event.
