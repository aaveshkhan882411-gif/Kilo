# AI Architecture

## AI Gateway

GrowthAI implements an AI Gateway abstraction layer to avoid hardcoding every agent to a single provider.

```
Agent → AI Gateway → Model Router → Provider Adapter → Inference
```

### Providers

| Provider | Environment | Status |
|----------|-------------|--------|
| Mock | Development | Implemented |
| vLLM | Production | Ready, requires GPU server |

### Model Router

The ModelRouter selects the appropriate provider based on:
- `AI_PROVIDER` environment variable
- Task type requirements
- Model requirements

### Agent Prompts

Each agent has a dedicated prompt template in `app/ai/prompts.py`.

### Agent Contracts

Every agent has a machine-readable contract containing:
- id, name, version
- purpose, capabilities, allowed_tools
- required_permissions
- input_schema, output_schema
- context_requirements, memory_policy
- safety_policy, execution_policy
- verification_policy, failure_policy
- audit_policy

### Development Without GPU

The application works in development with `AI_PROVIDER=mock`. The mock provider returns deterministic responses without requiring a GPU.

### Production GPU Deployment

When ready for production inference:
1. Set `AI_PROVIDER=vllm`
2. Configure `VLLM_BASE_URL` to point to your vLLM server
3. Set `VLLM_MODEL` to your model identifier
4. Set `VLLM_API_KEY` for authentication

The vLLM server should be deployed on dedicated GPU infrastructure with:
- Health checks
- Timeout handling
- Streaming support
- Fallback behavior
- Scaling strategy
