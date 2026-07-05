"""Bus de eventos en memoria para el stream SSE (un solo proceso)."""

import asyncio


class EventBus:
    def __init__(self, max_queue: int = 500) -> None:
        self._subscribers: set[asyncio.Queue] = set()
        self._max_queue = max_queue

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=self._max_queue)
        self._subscribers.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        self._subscribers.discard(q)

    def publish(self, event: dict) -> None:
        for q in list(self._subscribers):
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                # Cliente lento: se descarta el evento; SSE se recupera al
                # reconectar y pedir el estado completo.
                pass
