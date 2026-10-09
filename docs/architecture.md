# TruthLens AI - Architecture Specification

## Overview
TruthLens AI is an autonomous multi-agent misinformation investigation system. Rather than relying on simple prompt-response interactions, it executes a multi-step LangGraph workflow with deterministic confidence calculations, dynamic plan generation, prompt injection defense, and human-in-the-loop review.

## Architecture Diagram

```mermaid
graph TD
    User([User / Analyst]) --> UI[Next.js Dashboard & Trace UI]
    UI --> REST[FastAPI REST Endpoints]
    UI --> SSE[SSE Real-time Agent Trace]

    subgraph Backend Core Engine
        REST --> Auth[JWT & Database Session]
        REST --> Graph[LangGraph Multi-Agent Engine]

        subgraph LangGraph State Graph
            CA[Claim Analyzer Agent] --> IP[Planner Agent]
            IP --> RA[Research Agent & Tools]
            RA --> SE[Source Credibility Agent]
            SE --> EE[Evidence Extraction Agent]
            EE --> CD[Contradiction Detection Agent]
            CD --> CE[Deterministic Confidence Engine]
            CE --> VA[Verdict Agent]
            VA --> VerA[Verification Agent]
            VerA -- Revision Loop (Max 3) --> VA
            VerA -- High Contradiction / Low Score --> HR[Human Review Queue]
            VerA -- Verified --> RG[Report Generator]
        end

        Graph --> DB[(PostgreSQL / SQLite Database)]
        Graph --> Broadcaster[SSE Broadcaster]
        Broadcaster --> SSE
    end
```

## Core Subsystems
1. **LangGraph State Orchestrator**: Manages state transitions, retries, conditional branches, and persistent execution history.
2. **Deterministic Confidence Engine**: Calculates confidence scores based on weighted factors rather than LLM guesswork.
3. **Prompt Injection Defense**: Sanitizes scraped content by stripping injection triggers and isolating untrusted content inside XML boundaries.
4. **Interactive Evidence Graph**: Produces node-edge representations (Claim -> Sources -> Evidence -> Verdict) with relationship stances.
5. **Report Generation Service**: Produces HTML & PDF report packages.
