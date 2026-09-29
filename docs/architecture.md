# Architecture

```text
                         ┌───────────────────────┐
                         │     Streamlit UI      │
                         │ Command Center        │
                         │ Portfolio / Brief     │
                         │ Reflect Insights      │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │ Agent Orchestrator    │
                         └───────────┬───────────┘
                                     │
             ┌───────────────────────┼────────────────────────┐
             ▼                       ▼                        ▼
      Deal Historian          Executive Briefer         Risk Predictor
             │                       │                        │
             └───────────────────────┼────────────────────────┘
                                     ▼
                              Deal Memory Layer
                                     │
                       ┌─────────────┴─────────────┐
                       ▼                           ▼
               Local in-memory store       Hindsight HTTP API
                 (default fallback)          (optional remote)

      Objection Coach and Pattern Miner also query the same memory layer.
```

## Runtime behavior

1. The UI selects a deal and sends an action to an agent.
2. The agent queries the memory layer using the deal ID or user request.
3. Local mode uses a process-local store, so no external service is required.
4. When `HINDSIGHT_ENABLED=true`, the memory client attempts the configured Hindsight-compatible HTTP service.
5. If the remote service cannot be reached, the client safely falls back to local memory.

## Agent responsibilities

| Agent | Responsibility |
|---|---|
| Deal Historian | Retain and recall deal interactions |
| Executive Briefer | Assemble recalled deal context |
| Risk Predictor | Detect transparent risk signals |
| Objection Coach | Retrieve relevant objection context and draft a response |
| Pattern Miner | Explore recurring terms and create lightweight insights |
| Orchestrator | Route natural-language requests |

The current implementation deliberately keeps the risk and pattern components deterministic so their behavior is easy to inspect during a hackathon demo.
