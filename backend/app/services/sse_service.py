import asyncio
import json
import logging
from typing import Dict, Set
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

class SSEBroadcaster:
    """Broadcaster for real-time agent trace events via Server-Sent Events (SSE)."""

    def __init__(self):
        self._connections: Dict[str, Set[asyncio.Queue]] = {}

    def subscribe(self, investigation_id: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        if investigation_id not in self._connections:
            self._connections[investigation_id] = set()
        self._connections[investigation_id].add(queue)
        logger.info(f"Client subscribed to SSE for investigation: {investigation_id}")
        return queue

    def unsubscribe(self, investigation_id: str, queue: asyncio.Queue):
        if investigation_id in self._connections:
            self._connections[investigation_id].discard(queue)
            if not self._connections[investigation_id]:
                del self._connections[investigation_id]
        logger.info(f"Client unsubscribed from SSE for investigation: {investigation_id}")

    async def broadcast(self, investigation_id: str, event_type: str, data: dict):
        if investigation_id not in self._connections:
            return

        payload = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
        queues = list(self._connections[investigation_id])
        for q in queues:
            await q.put(payload)

sse_broadcaster = SSEBroadcaster()
