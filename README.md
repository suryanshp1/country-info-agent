# Country Info AI Agent (LangGraph)

## Features
- LangGraph agent pipeline
- REST Countries API integration
- Streaming responses
- Retry + timeout handling
- In-memory caching (TTL)
- LangSmith tracing

## Run locally

```bash
docker-compose up --build
```

Open:
[http://localhost:8000/docs](http://localhost:8000/docs)

## Example Query

POST /ask
```json
{
  "query": "What is the capital and population of India?"
}
```

## Architecture

User -> Intent Extraction -> Validation -> API Tool -> Processing -> Synthesis

## Production Features

* Retry logic (3 attempts)
* Timeout (5 sec)
* Caching (5 min TTL)
* Logging
* Graceful errors

## Limitations

* No fuzzy country matching
* LLM extraction may fail sometimes
* No persistent cache
