"""OpenJarvis automation blueprints — scheduled task system with real artifact output.

Mirrors and exceeds Hermes desktop cron/blueprint capabilities:
- 14 built-in automation blueprints (morning-brief, weekly-review, etc.)
- SQLite-backed persistent store for blueprint state
- Real artifact generation (markdown files, not placeholder text)
- Cron scheduler bridge for actual job execution
- CLI integration via `jarvis blueprint <command>`
"""
from __future__ import annotations

from openjarvis.blueprints.registry import BlueprintDefinition, BlueprintRegistry
from openjarvis.blueprints.store import BlueprintRecord, BlueprintStore
from openjarvis.blueprints.executor import BlueprintExecutor, BlueprintRunResult
from openjarvis.blueprints.scheduler_bridge import TaskSchedulerBridge

__all__ = [
    "BlueprintDefinition",
    "BlueprintRegistry", 
    "BlueprintRecord",
    "BlueprintStore",
    "BlueprintExecutor",
    "BlueprintRunResult",
    "TaskSchedulerBridge",
]
