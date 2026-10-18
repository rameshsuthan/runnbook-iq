---
document_id: guide-triage
title: Ambiguous symptom triage guide (synthetic)
service: order-api
document_type: guide
revision: '2026-10-18'
---
# Synthetic training document

## Clarifying a 503
If the only evidence is an order-api 503 or "orders are slow", ask for the request_id, affected interval, error identifier and process IDs. Then compare database acquisition waits with inventory request spans in that interval. Do not choose database exhaustion or dependency failure based on the caller-visible symptom alone.

## Evidence needed for a live cause
A current root cause requires current traces, metrics, deployment/configuration changes and dependency-side observations. This synthetic corpus supplies none of those live observations. State that the current cause is unknown and provide only documented investigative checks; do not state that a past incident is happening again.
