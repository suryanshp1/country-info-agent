from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from app.agent.graph import graph
import json
import asyncio

app = FastAPI(title="Country Info Agent")

# Allow Vite frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask(request: Request):
    body = await request.json()
    query = body.get("query", "")

    async def event_stream():
        # Stream LangGraph updates node by node
        async for output in graph.astream({"query": query}, stream_mode="updates"):
            for key, value in output.items():
                event_data = {
                    "node": key,
                    "state": value
                }
                yield f"data: {json.dumps(event_data)}\n\n"
            await asyncio.sleep(0.5) # Slight delay for UI visualization
            
        yield "event: end\ndata: \n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
