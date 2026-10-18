---
document_id: svc-order-api
title: Order API architecture (synthetic)
service: order-api
document_type: architecture
revision: '2026-10-18'
---
# Synthetic service architecture

## Request path
This document describes a fictional training service, not a real production system.
order-api validates an order, calls inventory-api to reserve stock, then opens a short PostgreSQL transaction to save the order. An inventory request should not hold a database connection. Every request has a request_id and trace_id. A caller-visible 503 alone cannot distinguish a database wait from a dependency timeout.

## Current configuration
Each order-api process has a PostgreSQL pool of 20 connections and a 500 ms pool-acquisition timeout. The inventory-api HTTP client has a 1500 ms request timeout. It does not automatically retry stock-reservation POST requests, because a timed-out request may already have committed a reservation. These values describe the synthetic current revision; historical incidents may have used other settings.

## Evidence boundaries
Runbooks document checks, not the state of a current incident. The corpus contains no live metrics, deployment history for today's event, customer records, passwords, host addresses, or real production credentials. Correlate errors by request_id and time window before comparing independent signals.
