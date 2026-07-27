"""
resilient_dispatcher.py
Unified King Wen 64-Hexagram Resilient Asynchronous WebSocket Event Dispatcher.

Domain Implementations:
- Async/Networking (Hex 5, 8, 13, 19): Non-Blocking Queueing & Broadcast Loop
- Database/Storage (Hex 2, 24, 48, 55): Shared Memory State Rehydration
- Scribe (Hex 17, 63): SHA-256 Provenance Audit Commit
- Dev / Refactoring (Hex 3, 18, 21, 62, 64): Complete Integrated Production Engine
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# ============================================================================
# 1. DATABASE/STORAGE DOMAIN: SHARED MEMORY STATE REHYDRATOR
# ============================================================================
class SharedMemoryStateRehydrator:
    """In-memory / Redis state rehydration pool for websocket sessions."""
    
    def __init__(self):
        self._storage_pool: Dict[str, Dict[str, Any]] = {}

    async def rehydrate_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self._storage_pool:
            logger.info("Initializing fresh session state for %s", session_id)
            self._storage_pool[session_id] = {
                "session_id": session_id,
                "created_at": time.time(),
                "event_count": 0,
                "last_active": time.time()
            }
        
        state = self._storage_pool[session_id]
        state["last_active"] = time.time()
        state["event_count"] += 1
        return state

    async def persist_state(self, session_id: str, state: Dict[str, Any]) -> None:
        self._storage_pool[session_id] = state

# ============================================================================
# 2. SCRIBE DOMAIN: IMMUTABLE SHA-256 AUDIT COMMIT
# ============================================================================
class ProvenanceScribe:
    """Generates immutable SHA-256 provenance commits for telemetry auditing."""
    
    @staticmethod
    def create_commit(packet_id: str, topic: str, save_string_hash: str) -> Dict[str, Any]:
        now = time.time()
        raw = f"{packet_id}:{topic}:{save_string_hash}:{now}"
        digest = hashlib.sha256(raw.encode('utf-8')).hexdigest()
        return {
            "packet_id": packet_id,
            "topic": topic,
            "timestamp": now,
            "save_string_hash": save_string_hash,
            "provenance_commit_sha256": digest
        }

# ============================================================================
# 3. ASYNC/NETWORKING & PRODUCTION DEV ENGINE
# ============================================================================
class ResilientWebSocketDispatcher:
    """Production Async WebSocket Event Dispatcher Engine."""
    
    def __init__(self, max_queue_size: int = 1000):
        self.rehydrator = SharedMemoryStateRehydrator()
        self.scribe = ProvenanceScribe()
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.subscribers: Dict[str, List[Callable[[Dict[str, Any]], Any]]] = {}
        self.is_running = False

    def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], Any]) -> None:
        self.subscribers.setdefault(topic, []).append(handler)

    async def ingest_packet(self, packet: Dict[str, Any], chaos_level: float = 0.2) -> Dict[str, Any]:
        # High Chaos Protection Check
        if chaos_level > 0.70:
            raise RuntimeError(f"CHAOS_ELEVATION_EXCEEDED: Ingress dropped (chaos={chaos_level:.3f})")

        # Rehydrate Session State
        session_id = packet.get("sessionId", "anonymous")
        session_state = await self.rehydrator.rehydrate_session(session_id)

        # Generate Provenance Commit
        commit = self.scribe.create_commit(packet["id"], packet["topic"], "KW64_V2.0_HASH")

        result = {
            "status": "ingested",
            "packet": packet,
            "session_state": session_state,
            "provenance": commit
        }

        await self.queue.put(result)
        return result

    async def run_dispatch_loop(self):
        self.is_running = True
        logger.info("Resilient WebSocket Dispatcher loop started.")
        while self.is_running:
            item = await self.queue.get()
            packet = item["packet"]
            topic = packet.get("topic")
            
            handlers = self.subscribers.get(topic, [])
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(item)
                    else:
                        handler(item)
                except Exception as exc:
                    logger.error("Handler error for topic %s: %s", topic, exc)

            self.queue.task_done()

# ============================================================================
# 4. VERIFICATION HARNESS
# ============================================================================
async def main():
    dispatcher = ResilientWebSocketDispatcher()

    # Register subscriber
    received_packets = []
    async def sample_handler(data):
        received_packets.append(data)
        print(f"[SUBSCRIBER RECEIVED]: Packet {data['packet']['id']} on topic '{data['packet']['topic']}'")

    dispatcher.subscribe("user.events", sample_handler)

    # Launch loop in background
    dispatch_task = asyncio.create_task(dispatcher.run_dispatch_loop())

    # Ingest test packets
    packet1 = {
        "id": "pkt_001",
        "topic": "user.events",
        "payload": {"user_id": 42, "action": "login"},
        "timestamp": time.time(),
        "sessionId": "sess_alpha"
    }

    res = await dispatcher.ingest_packet(packet1, chaos_level=0.15)
    print("Ingress Result:", json.dumps(res, indent=2))

    # Wait for queue execution
    await asyncio.sleep(0.1)
    dispatcher.is_running = False
    await dispatch_task

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
