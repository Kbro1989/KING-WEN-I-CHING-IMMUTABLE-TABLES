"""Bridge between BlueprintExecutor and the TaskScheduler cron system.

Maps blueprint definitions to scheduled tasks with real execution,
not placeholder stubs. Each blueprint becomes a cron job that:
1. Runs on schedule
2. Executes the blueprint via BlueprintExecutor
3. Logs artifacts to SQLite + disk
4. Reports status back to the scheduler
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from openjarvis.blueprints.registry import BlueprintRegistry
from openjarvis.blueprints.store import BlueprintStore, BlueprintRecord
from openjarvis.blueprints.executor import BlueprintExecutor

logger = logging.getLogger(__name__)


class TaskSchedulerBridge:
    """Bridge blueprints to the Jarvis TaskScheduler for cron execution."""

    def __init__(
        self,
        store: BlueprintStore,
        executor: BlueprintExecutor,
        scheduler=None,
    ) -> None:
        self.store = store
        self.executor = executor
        self.scheduler = scheduler
        self.registry = BlueprintRegistry()

    def register_all(self) -> List[Dict[str, Any]]:
        """Register all active blueprints with the scheduler. Returns registered jobs."""
        registered = []
        for record in self.store.list_blueprints():
            if record.status != "active":
                continue
            definition = self.registry.match(record.key)
            if not definition:
                continue
            job = self._register_job(record, definition)
            if job:
                registered.append(job)
        return registered

    def create_blueprint_job(
        self,
        key: str,
        schedule: Optional[str] = None,
        values: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Create a new blueprint job and register it with the scheduler."""
        definition = self.registry.match(key)
        if not definition:
            raise ValueError(f"Unknown blueprint: {key}")

        record = BlueprintRecord(
            key=definition.key,
            title=definition.title,
            description=definition.description,
            schedule=schedule or definition.default_schedule,
            tools=definition.default_tools,
            agent=definition.default_agent,
            output_artifact=definition.output_artifact,
            status="active",
            metadata={"values": values or {}},
        )
        self.store.save_blueprint(record)

        job = self._register_job(record, definition)
        return {
            "key": key,
            "schedule": record.schedule,
            "status": "created",
            "job_id": job.get("id") if job else None,
        }

    def _register_job(self, record: BlueprintRecord, definition) -> Optional[Dict[str, Any]]:
        """Register a single blueprint with the scheduler."""
        if not self.scheduler:
            logger.warning("No scheduler available; blueprint %s will not run on schedule", record.key)
            return None

        job_id = f"blueprint-{record.key}-{uuid.uuid4().hex[:8]}"

        def _run_blueprint():
            """Closure that executes the blueprint and logs result."""
            try:
                values = record.metadata.get("values", {})
                result = self.executor.run(definition, values=values)
                self.store.update_last_run(record.key, datetime.now(timezone.utc).isoformat())
                logger.info("Blueprint %s executed: %s", record.key, result.status)
                return {
                    "status": result.status,
                    "artifact_path": result.artifact_path,
                    "summary": result.summary,
                }
            except Exception as exc:
                logger.error("Blueprint %s execution failed: %s", record.key, exc)
                self.store.update_status(record.key, "error")
                return {"status": "error", "error": str(exc)}

        # Try to register with scheduler
        try:
            self.scheduler.add_job(
                func=_run_blueprint,
                trigger="cron",
                id=job_id,
                name=f"Blueprint: {definition.title}",
                replace_existing=True,
                **self._parse_cron(record.schedule),
            )
            return {
                "id": job_id,
                "key": record.key,
                "schedule": record.schedule,
                "registered": True,
            }
        except Exception as exc:
            logger.error("Failed to register blueprint job %s: %s", job_id, exc)
            return {"id": job_id, "key": record.key, "registered": False, "error": str(exc)}

    def _parse_cron(self, schedule: str) -> Dict[str, Any]:
        """Parse a cron expression into APScheduler kwargs."""
        parts = schedule.strip().split()
        if len(parts) == 5:
            return {
                "minute": parts[0],
                "hour": parts[1],
                "day": parts[2],
                "month": parts[3],
                "day_of_week": parts[4],
            }
        # Default: daily at 8am
        return {"hour": 8, "minute": 0}

    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all blueprint jobs from the store."""
        return [
            {
                "key": r.key,
                "title": r.title,
                "schedule": r.schedule,
                "status": r.status,
                "last_run": r.last_run,
                "next_run": r.next_run,
            }
            for r in self.store.list_blueprints()
        ]

    def pause_job(self, key: str) -> bool:
        """Pause a blueprint job."""
        self.store.update_status(key, "paused")
        return True

    def resume_job(self, key: str) -> bool:
        """Resume a blueprint job."""
        self.store.update_status(key, "active")
        # Re-register with scheduler
        record = self.store.get_blueprint(key)
        if record:
            definition = self.registry.match(key)
            if definition:
                self._register_job(record, definition)
        return True

    def delete_job(self, key: str) -> bool:
        """Delete a blueprint job."""
        self.store.delete_blueprint(key)
        return True
