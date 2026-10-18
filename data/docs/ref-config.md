---
document_id: ref-config
title: Current configuration reference (synthetic)
service: order-api
document_type: reference
revision: '2026-10-18'
---
# Synthetic training document

## Current limits
As of the synthetic 2026-10-18 revision, order-api uses a PostgreSQL pool limit of 20 connections per process and a 500 ms acquisition timeout. The inventory-api request deadline is 1500 ms. These are distinct settings; the corpus contains no universal recommended production values. The stock-reservation client performs zero automatic retries.

## Historical comparison
The 2026-09-04 pool incident involved a historical per-process pool limit of 12. The current limit of 20 came from a separate capacity review. The incident correction was acquiring a connection after the inventory request, not a blanket recommendation to enlarge pools. Always compare the revision and process scope before treating historical configuration as current.
