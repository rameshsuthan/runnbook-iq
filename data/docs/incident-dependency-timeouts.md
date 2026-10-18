---
document_id: incident-dependency-timeouts
title: Inventory path latency incident (synthetic)
service: order-api
document_type: incident
revision: '2026-10-18'
---
# Synthetic training document

## Timeline
Historical synthetic incident on 2026-10-02, all times UTC. At 14:00 inventory request latency increased after a network routing change. At 14:06 dependency spans showed long connection-establishment time while database pool acquisition remained normal. The routing change was reverted at 14:12. By 14:20 inventory request durations returned to baseline.

## Findings and scope
For this historical event, the investigation attributed the delays to the changed network route. The client deadline was 1500 ms. Operators correlated caller spans with the routing change before reverting it. No evidence in this report establishes the cause of today's timeout, and a timeout alone cannot identify network routing as the cause. No automatic stock-reservation retry was introduced.
