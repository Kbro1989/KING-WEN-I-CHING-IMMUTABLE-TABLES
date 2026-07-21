# OpenJarvis Blueprint Integration Guide

## Files to Install

Copy these files into your OpenJarvis source tree:

```
src/openjarvis/blueprints/
├── __init__.py           ← Package init (exports all public APIs)
├── registry.py           ← Already exists, verified
├── store.py              ← Already exists, verified  
├── executor.py           ← Already exists, verified
├── scheduler_bridge.py   ← NEW: Cron scheduler bridge
└── cmd.py                ← NEW: CLI command group
```

## Chat Command Integration

Replace the `/blueprint` handler block in `src/openjarvis/cli/chat_cmd.py`
(~line 464) with this real execution path:

```python
        elif cmd.startswith("/blueprint "):
            query = user_input[len("/blueprint "):].strip()
            if not query:
                console.print("[yellow]Usage: /blueprint <name>|catalog|list|run <name>|pause <name>|resume <name>|delete <name>[/yellow]")
                continue

            from openjarvis.blueprints.registry import BlueprintRegistry
            from openjarvis.blueprints.store import BlueprintStore
            from openjarvis.blueprints.executor import BlueprintExecutor
            from openjarvis.blueprints.scheduler_bridge import TaskSchedulerBridge
            from pathlib import Path

            DB_PATH = Path.home() / ".openjarvis" / "blueprints.db"
            ARTIFACTS_ROOT = Path.home() / ".openjarvis" / "artifacts" / "blueprints"
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)

            store = BlueprintStore(DB_PATH)
            executor = BlueprintExecutor(store, artifacts_root=str(ARTIFACTS_ROOT))
            bridge = TaskSchedulerBridge(store, executor)
            registry = BlueprintRegistry()

            parts = query.split(maxsplit=1)
            subcmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if subcmd == "catalog":
                console.print("[bold]Available Blueprints:[/bold]")
                for bp in registry.list_all():
                    status = "[green]✓[/green]" if bp.actionable else "[dim]○[/dim]"
                    console.print(f"  {status} [cyan]{bp.key}[/cyan] — {bp.title}")
                    console.print(f"    [dim]{bp.description}[/dim]")

            elif subcmd == "list":
                jobs = bridge.list_jobs()
                if not jobs:
                    console.print("[dim]No blueprint jobs configured.[/dim]")
                else:
                    console.print(f"[bold]{'Key':20s} {'Status':10s} {'Schedule':20s} {'Last Run'}[/bold]")
                    for job in jobs:
                        last = job.get("last_run") or "Never"
                        console.print(f"{job['key']:20s} {job['status']:10s} {job['schedule']:20s} {last}")

            elif subcmd == "create" and arg:
                definition = registry.match(arg)
                if not definition:
                    console.print(f"[red]Unknown blueprint: {arg}[/red]")
                    continue
                result = bridge.create_blueprint_job(key=definition.key)
                console.print(f"[green]Created:[/green] {result['key']} @ {result['schedule']}")

            elif subcmd == "run" and arg:
                definition = registry.match(arg)
                if not definition:
                    console.print(f"[red]Unknown blueprint: {arg}[/red]")
                    continue
                result = executor.run(definition)
                console.print(f"[green]Executed:[/green] {result.status}")
                if result.artifact_path:
                    console.print(f"  Artifact: [cyan]{result.artifact_path}[/cyan]")

            elif subcmd == "pause" and arg:
                bridge.pause_job(arg)
                console.print(f"[yellow]Paused:[/yellow] {arg}")

            elif subcmd == "resume" and arg:
                bridge.resume_job(arg)
                console.print(f"[green]Resumed:[/green] {arg}")

            elif subcmd == "delete" and arg:
                bridge.delete_job(arg)
                console.print(f"[red]Deleted:[/red] {arg}")

            else:
                # Legacy: treat as blueprint query via oracle
                console.print(f"[dim]Unknown subcommand '{subcmd}'. Try: catalog, list, create, run, pause, resume, delete[/dim]")
```

## CLI Integration

Add to your `jarvis` CLI entry point (where other command groups are registered):

```python
from openjarvis.blueprints.cmd import blueprint_cli
# In your main click group:
cli.add_command(blueprint_cli)
```

## Verification Commands

```bash
# 1. Verify blueprints compile
python -m py_compile src/openjarvis/blueprints/*.py

# 2. Test catalog
python -c "from openjarvis.blueprints.registry import BlueprintRegistry; r=BlueprintRegistry(); print(len(r.list_all()), 'blueprints')"

# 3. Test store + executor
python -c "
from openjarvis.blueprints.store import BlueprintStore
from openjarvis.blueprints.executor import BlueprintExecutor
from openjarvis.blueprints.registry import BlueprintRegistry
import tempfile, os
with tempfile.TemporaryDirectory() as td:
    store = BlueprintStore(os.path.join(td, 'test.db'))
    executor = BlueprintExecutor(store, artifacts_root=td)
    reg = BlueprintRegistry()
    bp = reg.match('morning-brief')
    result = executor.run(bp)
    print('Status:', result.status)
    print('Artifact:', result.artifact_path)
    print('Has content:', os.path.exists(result.artifact_path) if result.artifact_path else False)
"

# 4. Test scheduler bridge (without scheduler)
python -c "
from openjarvis.blueprints.scheduler_bridge import TaskSchedulerBridge
from openjarvis.blueprints.store import BlueprintStore
from openjarvis.blueprints.executor import BlueprintExecutor
import tempfile
with tempfile.TemporaryDirectory() as td:
    store = BlueprintStore(os.path.join(td, 'test.db'))
    executor = BlueprintExecutor(store, artifacts_root=td)
    bridge = TaskSchedulerBridge(store, executor)
    jobs = bridge.list_jobs()
    print('Jobs:', len(jobs))
"
```

## What This Gives You (vs Hermes Desktop)

| Capability | Hermes Desktop | OpenJarvis (this build) |
|---|---|---|
| Blueprint catalog | ✓ React UI | ✓ CLI + chat_cmd |
| Scheduled execution | ✓ Cron UI | ✓ APScheduler bridge |
| Real artifacts | ✓ File output | ✓ Markdown files on disk |
| Persistent state | ✓ SQLite | ✓ SQLite store |
| Pause/resume | ✓ UI buttons | ✓ CLI + chat commands |
| Job status | ✓ Visual indicators | ✓ CLI table + chat output |
| Learning log | ✓ Per-agent | ✓ Per-blueprint artifact logs |
| 14 built-ins | ✓ | ✓ (morning-brief through on-this-day) |
