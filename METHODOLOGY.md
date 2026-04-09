# MDA Intent Layer --- Methodology

## Executive Summary

The MDA Intent Layer is a model transformation pipeline that produces structured artifacts for AI agentic software development. The pipeline transforms BPMN process models into machine-executable intent specifications and integration contracts --- a triple of artifacts that together give an AI agent everything it needs to perform a business task without human intervention.

The transformation chain is governed by the OMG's Model-Driven Architecture (MDA). MDA provides the theoretical backbone: BPMN diagrams serve as the Computation-Independent Model, intent specifications serve as the Platform-Independent Model, and integration contracts serve as the Platform-Specific Model. Each transformation is deterministic, auditable, and reversible.

This document is intended for enterprise architects, platform engineers, and methodology reviewers who need to understand the theoretical foundation, the design constraints, and the lifecycle governance of the intent layer's artifacts.

## Why MDA

MDA's three-layer abstraction maps directly to the three artifacts this pipeline produces:

- **CIM (Computation-Independent Model) = BPMN diagram.** The BPMN model describes what the business does in pure business terms. It contains no technology choices, no API references, no platform assumptions. It is owned by business analysts and changes on an annual cadence.

- **PIM (Platform-Independent Model) = Intent Specification.** The intent spec describes what outcome must be achieved for a given BPMN task. It names the goal, the preconditions, the postconditions, the outcome verification criteria, and the forbidden actions --- all without binding to any specific API, SDK, or runtime. It is platform-independent by construction.

- **PSM (Platform-Specific Model) = Integration Contract.** The integration contract binds the intent spec to a concrete execution environment: API endpoints, event schemas, authentication mechanisms, rate limits, retry policies, error mappings. It is the only artifact that contains technology-specific detail.

The **Knowledge Capsule** extends MDA as a companion to the PIM. It encodes the domain knowledge an agent needs to interpret the intent spec correctly --- business rules, edge cases, regulatory constraints, terminology --- in a format readable by both humans and AI agents. The capsule is not a fourth MDA layer; it is supplementary context that travels alongside the PIM.

MDA brings over twenty years of OMG standardization, broad enterprise architect familiarity, and a proven track record in model transformation. These properties make the methodology immediately legible to governance boards, architecture review committees, and standards bodies without requiring them to learn a novel framework.

## Why MDA Over Other Methodologies

Several AI development methodologies were evaluated for this pipeline, including BMAD (an AI agent collaboration framework). BMAD defines agent personas, story and epic structures, development workflows, and collaboration patterns for teams of AI agents building software together. It solves the problem of "how do AI agents collaborate to build software."

The problem this pipeline solves is different: "how do we transform business process models into machine-executable intent specifications." This is a model transformation problem, not a software development workflow problem. It requires a framework that governs abstraction layers, transformation rules, and artifact traceability --- exactly what MDA provides.

Applying an agent collaboration framework to the transformation pipeline would be a category error. Such frameworks have no concept of CIM-to-PIM transformation, no formal abstraction layers, and no model traceability semantics. Conversely, MDA has no concept of agent personas or development sprints. MDA was selected because it directly addresses the core challenge: structured, auditable model transformation.

## The Hybrid Approach

The architecture combines two frameworks, each applied to the problem it was designed to solve:

- **MDA** provides the backbone for the transformation pipeline. Every artifact maps to an MDA abstraction layer. Every transformation between layers follows MDA's rules for traceability and reversibility.

- **DDD (Domain-Driven Design)** provides bounded contexts for process isolation. Each repository corresponds to one bounded context. Cross-context dependencies are explicit and managed through integration contracts, never through shared internal models.

To maintain clarity and avoid overloading MDA terminology in day-to-day use, the pipeline uses its own naming conventions:

| MDA Term | Pipeline Term | Description |
|----------|---------------|-------------|
| CIM companion | Knowledge Capsule | Domain knowledge for agent consumption |
| PIM | Intent Specification | Platform-independent outcome definition |
| PSM | Integration Contract | Platform-specific API and event bindings |

## Core Principles

1. **One BPMN Task = One Triple.** Every task in the BPMN diagram produces exactly one triple: one intent spec, one integration contract, one capsule. No merging of tasks into a single spec. No splitting of a task across multiple specs. The mapping is strict and 1:1.

2. **Anti-UI Principle.** Intent specifications must never be satisfied through browser automation, screen scraping, UI clicks, or any form of graphical interface interaction. If the only path to fulfillment is through a UI, the integration contract is incomplete and must be flagged for remediation.

3. **Separation of Change Rates.** Each layer in the pipeline changes at its own cadence. BPMN models change annually. Knowledge capsules change quarterly. Intent specifications change quarterly. Integration contracts change monthly. Agent runtime implementations change weekly. The architecture enforces this separation so that a change in one layer does not force a cascade through every other layer.

4. **Conservative Enrichment.** When transforming between layers, the pipeline must flag gaps rather than fabricate content. A draft triple with honest gaps --- clearly marked as unresolved --- is always preferable to a complete triple with hallucinated business rules, invented API endpoints, or assumed preconditions.

5. **Artifacts for Agents.** Every triple is designed to be consumed by an AI agent, not merely read by a human. The intent spec is the task brief. The capsule is domain knowledge. The contract is the API reference. Together they form a self-contained work package.

6. **Governed Lifecycle.** All triples follow a managed lifecycle: **draft**, **review**, **approved**, **current**, **deprecated**, **archived**. Transitions are enforced by Git workflow. No artifact reaches production without passing through review. No artifact is deleted --- it is archived, preserving full audit history.

## Glossary

| Term | Definition |
|------|------------|
| **Anti-UI Principle** | The constraint that intent specs must never be fulfilled through browser automation, screen scraping, or UI interaction. |
| **Bounded Context** | A DDD concept defining a boundary within which a domain model is consistent and self-contained. In this pipeline, one repository equals one bounded context. |
| **Capsule (Knowledge Capsule)** | A structured document encoding domain knowledge --- business rules, edge cases, regulatory constraints, terminology --- for both human and agent consumption. Companion to the intent spec. |
| **CIM (Computation-Independent Model)** | The MDA abstraction layer describing business processes without technology. Mapped to BPMN diagrams in this pipeline. |
| **Forbidden Action** | An explicitly prohibited behavior listed in an intent spec. Agents must not perform forbidden actions even if doing so would achieve the stated outcome. |
| **Integration Contract** | The platform-specific artifact binding an intent spec to concrete APIs, event schemas, authentication, and error handling. Maps to the PSM in MDA. |
| **Intent Spec (Intent Specification)** | The platform-independent artifact defining what outcome must be achieved, under what preconditions, with what verification criteria. Maps to the PIM in MDA. |
| **Outcome Verification** | The set of observable conditions that confirm an intent spec has been fulfilled. Defined in the intent spec, executed by the agent runtime. |
| **PIM (Platform-Independent Model)** | The MDA abstraction layer describing system behavior without platform bindings. Mapped to intent specifications in this pipeline. |
| **PSM (Platform-Specific Model)** | The MDA abstraction layer describing system behavior bound to a specific platform. Mapped to integration contracts in this pipeline. |
| **Triple** | The complete artifact set for one BPMN task: one intent spec, one integration contract, one knowledge capsule. The atomic unit of work in this pipeline. |
