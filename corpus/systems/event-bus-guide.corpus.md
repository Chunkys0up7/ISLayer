---
corpus_id: "CRP-SYS-MTG-003"
title: "Event Bus Integration Guide"
slug: "event-bus-guide"
doc_type: "system"
domain: "Mortgage Lending"
subdomain: "Core Systems"
tags:
  - system
  - integration
  - event-bus
  - kafka
  - event-driven
  - messaging
applies_to:
  process_ids:
    - "PRC-MTG-ORIG-001"
    - "PRC-MTG-INCV-001"
    - "PRC-MTG-APPR-001"
  task_types:
    - origination
    - verification
    - appraisal
    - event_processing
    - system_integration
  task_name_patterns:
    - "*_event_*"
    - "*_publish_*"
    - "*_subscribe_*"
  goal_types:
    - integration
    - event_processing
    - automation
  roles:
    - system_administrator
    - developer
    - loan_processor
version: "1.0"
status: "current"
effective_date: "2026-01-01"
review_date: "2026-07-01"
supersedes: null
superseded_by: null
author: "MDA Demo"
last_modified: "2026-04-09"
last_modified_by: "MDA Demo"
source: "internal"
source_ref: null
related_corpus_ids:
  - "CRP-SYS-MTG-001"
  - "CRP-SYS-MTG-002"
regulation_refs: []
policy_refs: []
---

# Event Bus Integration Guide

## System Overview

The enterprise event bus is a Kafka-based event streaming platform that enables real-time, asynchronous communication between mortgage lending systems. It provides reliable, ordered event delivery with exactly-once semantics, enabling loosely coupled integration between the LOS, DocVault, compliance systems, and external service providers.

### Architecture Principles

- **Event Sourcing**: All state changes in core systems are captured as immutable events, providing a complete audit trail and enabling event replay for debugging and reprocessing.
- **Topic-per-Domain**: Events are organized into topics by source domain (e.g., `los.loan.*`, `docvault.document.*`), enabling fine-grained subscription and access control.
- **Schema Registry**: All event schemas are registered in a central Avro Schema Registry with compatibility enforcement (backward compatible by default).
- **Consumer Groups**: Each consuming service uses a dedicated consumer group for independent offset management, enabling parallel processing and fault isolation.
- **Dead Letter Queues**: Failed messages are routed to DLQ topics after configurable retry attempts, with alerting and manual reprocessing capabilities.

### Infrastructure

```
Bootstrap Servers:
  Production:  kafka-prod-1.internal:9093,kafka-prod-2.internal:9093,kafka-prod-3.internal:9093
  Staging:     kafka-staging-1.internal:9093

Schema Registry:
  Production:  https://schema-registry.internal:8443
  Staging:     https://schema-registry-staging.internal:8443
```

## Topics

### Naming Convention

Topics follow the pattern: `{domain}.{entity}.{action}`

Examples: `los.loan.created`, `docvault.document.uploaded`, `verification.income.completed`

### Topic Configuration

| Topic Pattern | Partitions | Replication | Retention | Compaction |
|--------------|-----------|-------------|-----------|------------|
| `los.loan.*` | 12 | 3 | 30 days | No |
| `los.borrower.*` | 6 | 3 | 30 days | No |
| `los.condition.*` | 6 | 3 | 30 days | No |
| `docvault.document.*` | 12 | 3 | 30 days | No |
| `docvault.extraction.*` | 6 | 3 | 14 days | No |
| `verification.income.*` | 6 | 3 | 30 days | No |
| `verification.employment.*` | 6 | 3 | 30 days | No |
| `appraisal.*` | 6 | 3 | 30 days | No |
| `compliance.*` | 6 | 3 | 90 days | No |
| `*.dlq` | 3 | 3 | 90 days | No |
| `audit.*` | 12 | 3 | 365 days | Log compaction |

### Partitioning Strategy

All loan-related events are partitioned by `loanId` to ensure ordered processing of events for the same loan. This guarantees that all events for a given loan are processed sequentially within a single partition, maintaining causal ordering.

```
Partition Key: loanId (hashed)
```

## Schemas (Avro)

### Standard Event Envelope

Every event is wrapped in a standard envelope that provides metadata for tracing, auditing, and routing.

```json
{
  "type": "record",
  "name": "EventEnvelope",
  "namespace": "com.lendingplatform.events",
  "fields": [
    { "name": "eventId", "type": "string", "doc": "Globally unique event identifier (UUID v4)" },
    { "name": "eventType", "type": "string", "doc": "Fully qualified event type (e.g., los.loan.created)" },
    { "name": "eventVersion", "type": "string", "default": "1.0", "doc": "Schema version of the event payload" },
    { "name": "timestamp", "type": "long", "logicalType": "timestamp-millis", "doc": "Event creation timestamp in UTC milliseconds" },
    { "name": "sourceSystem", "type": "string", "doc": "System that produced the event" },
    { "name": "correlationId", "type": "string", "doc": "Correlation ID for request tracing across services" },
    { "name": "causationId", "type": ["null", "string"], "default": null, "doc": "Event ID of the event that caused this event" },
    { "name": "actorId", "type": ["null", "string"], "default": null, "doc": "User or service that triggered the event" },
    { "name": "loanId", "type": ["null", "string"], "default": null, "doc": "Associated loan identifier (partition key)" },
    { "name": "payload", "type": "bytes", "doc": "Avro-encoded event-specific payload" }
  ]
}
```

### Example: Loan Status Changed Event

```json
{
  "type": "record",
  "name": "LoanStatusChangedPayload",
  "namespace": "com.lendingplatform.events.los",
  "fields": [
    { "name": "loanId", "type": "string" },
    { "name": "previousStatus", "type": "string" },
    { "name": "newStatus", "type": "string" },
    { "name": "previousMilestone", "type": ["null", "string"], "default": null },
    { "name": "newMilestone", "type": "string" },
    { "name": "reason", "type": ["null", "string"], "default": null },
    { "name": "triggeredBy", "type": "string", "doc": "User ID or system that triggered the change" },
    { "name": "conditions", "type": { "type": "array", "items": "string" }, "default": [], "doc": "Outstanding condition IDs if applicable" }
  ]
}
```

### Example: Income Verification Completed Event

```json
{
  "type": "record",
  "name": "IncomeVerificationCompletedPayload",
  "namespace": "com.lendingplatform.events.verification",
  "fields": [
    { "name": "loanId", "type": "string" },
    { "name": "borrowerId", "type": "string" },
    { "name": "verificationType", "type": "string", "doc": "W2, PAYSTUB, TAX_RETURN, VOE, VERBAL_VOE" },
    { "name": "verificationResult", "type": "string", "doc": "VERIFIED, DISCREPANCY, UNABLE_TO_VERIFY" },
    { "name": "reportedMonthlyIncomeCents", "type": "long" },
    { "name": "verifiedMonthlyIncomeCents", "type": "long" },
    { "name": "variancePercent", "type": "double" },
    { "name": "documentIds", "type": { "type": "array", "items": "string" } },
    { "name": "verifiedBy", "type": "string" },
    { "name": "notes", "type": ["null", "string"], "default": null }
  ]
}
```

## Delivery Guarantees

### Producer Configuration

- **Acknowledgment**: `acks=all` (wait for all in-sync replicas)
- **Retries**: 3 retries with exponential backoff (100ms, 200ms, 400ms)
- **Idempotence**: Enabled (`enable.idempotence=true`) for exactly-once producer semantics
- **Max In-Flight**: 5 requests per connection (safe with idempotence enabled)
- **Serialization**: Avro with Schema Registry for key and value

### Consumer Configuration

- **Auto Commit**: Disabled. Manual offset commit after successful processing.
- **Isolation Level**: `read_committed` for transactional message support
- **Max Poll Records**: 100 per poll
- **Session Timeout**: 30 seconds
- **Heartbeat Interval**: 10 seconds
- **Max Poll Interval**: 5 minutes (processing deadline per batch)

### Error Handling

1. **Transient Errors**: Automatic retry with exponential backoff (max 3 attempts)
2. **Deserialization Errors**: Route to DLQ immediately (no retry)
3. **Processing Errors**: Retry up to 3 times, then route to DLQ with error metadata
4. **DLQ Structure**: `{original-topic}.dlq` contains the original message plus error details
5. **Alerting**: DLQ messages trigger PagerDuty alerts for the owning team

### Consumer Groups

| Consumer Group ID | Source Topics | Processing Service |
|-------------------|--------------|-------------------|
| `income-verification-svc` | `los.borrower.*`, `docvault.extraction.completed` | Income Verification Service |
| `appraisal-mgmt-svc` | `los.appraisal.*`, `los.property.*` | Appraisal Management Service |
| `compliance-monitor` | `los.loan.*`, `los.disclosure.*` | Compliance Monitoring Service |
| `underwriting-svc` | `verification.*`, `appraisal.*`, `los.condition.*` | Underwriting Service |
| `audit-logger` | `*` (all topics) | Audit Log Service |
| `notification-svc` | `los.loan.status.changed`, `los.condition.*` | Borrower Notification Service |
| `analytics-pipeline` | `*` (all topics) | Data Warehouse ETL |

## Monitoring

### Key Metrics

- **Consumer Lag**: Maximum acceptable lag is 1,000 messages per partition. Alerts fire at 5,000.
- **DLQ Rate**: Target is less than 0.01% of total messages. Alerts fire at 0.1%.
- **End-to-End Latency**: P99 target is under 500ms from produce to consume. Alerts fire at 2 seconds.
- **Partition Skew**: No single partition should hold more than 2x the average message count.

### Health Check Endpoint

```
GET https://event-bus-admin.internal/health
GET https://event-bus-admin.internal/topics/{topicName}/lag
GET https://event-bus-admin.internal/consumer-groups/{groupId}/status
```
