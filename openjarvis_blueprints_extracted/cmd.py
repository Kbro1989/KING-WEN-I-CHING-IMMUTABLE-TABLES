"""CLI commands for Jarvis automation blueprints.

Usage:
    jarvis blueprint catalog          # List all available blueprints
    jarvis blueprint create <name>    # Create and schedule a blueprint
    jarvis blueprint list             # List active blueprint jobs
    jarvis blueprint run <name>       # Run a blueprint immediately
    jarvis blueprint pause <name>     # Pause a scheduled blueprint
    jarvis blueprint resume <name>    # Resume a paused blueprint
    jarvis blueprint delete <name>    # Delete a blueprint job
"""
from __future__ import annotations

import click
from pathlib import Path

from openjarvis.blueprints.registry import BlueprintRegistry
from openjarvis.blueprints.store import BlueprintStore
from openjarvis.blueprints.executor import BlueprintExecutor
from openjarvis.blueprints.scheduler_bridge import TaskSchedulerBridge


DEFAULT_DB = Path.home() / ".openjarvis" / "blueprints.db"
DEFAULT_ARTIFACTS = Path.home() / ".openjarvis" / "artifacts" / "blueprints"


def _get_store() -> BlueprintStore:
    DEFAULT_DB.parent.mkdir(parents=True, exist_ok=True)
    return BlueprintStore(DEFAULT_DB)


def _get_executor() -> BlueprintExecutor:
    return BlueprintExecutor(_get_store(), artifacts_root=str(DEFAULT_ARTIFACTS))


def _get_bridge() -> TaskSchedulerBridge:
    return TaskSchedulerBridge(_get_store(), _get_executor())


@click.group("blueprint")
def blueprint_cli():
    """Manage Jarvis automation blueprints."""
    pass


@blueprint_cli.command("catalog")
def blueprint_catalog():
    """List all available blueprint definitions."""
    registry = BlueprintRegistry()
    click.echo("Available Blueprints:")
    click.echo("-" * 50)
    for bp in registry.list_all():
        status = "✓" if bp.actionable else "○"
        click.echo(f"  {status} {bp.key:20s} — {bp.title}")
        click.echo(f"    {bp.description}")
        click.echo(f"    Schedule: {bp.default_schedule} | Agent: {bp.default_agent}")
        click.echo()


@blueprint_cli.command("create")
@click.argument("name")
@click.option("--schedule", "-s", help="Cron schedule expression (default: blueprint default)")
@click.option("--agent", "-a", default="simple", help="Agent type to run blueprint")
@click.option("--tools", "-t", help="Comma-separated tool list")
@click.option("--text", help="Custom reminder text (for custom-reminder blueprint)")
def blueprint_create(name: str, schedule: str, agent: str, tools: str, text: str):
    """Create and schedule a blueprint job."""
    registry = BlueprintRegistry()
    definition = registry.match(name)
    if not definition:
        click.echo(f"Error: No blueprint matches '{name}'.")
        click.echo("Run `jarvis blueprint catalog` for available blueprints.")
        raise click.BadParameter(name)

    bridge = _get_bridge()
    values = {}
    if text:
        values["text"] = text

    result = bridge.create_blueprint_job(
        key=definition.key,
        schedule=schedule or definition.default_schedule,
        values=values,
    )
    click.echo(f"Created blueprint job: {result['key']}")
    click.echo(f"  Schedule: {result['schedule']}")
    click.echo(f"  Status: {result['status']}")
    if result.get("job_id"):
        click.echo(f"  Job ID: {result['job_id']}")


@blueprint_cli.command("list")
def blueprint_list():
    """List all active blueprint jobs."""
    bridge = _get_bridge()
    jobs = bridge.list_jobs()
    if not jobs:
        click.echo("No blueprint jobs configured.")
        return
    click.echo(f"{'Key':20s} {'Status':10s} {'Schedule':20s} {'Last Run'}")
    click.echo("-" * 70)
    for job in jobs:
        last = job.get("last_run") or "Never"
        click.echo(f"{job['key']:20s} {job['status']:10s} {job['schedule']:20s} {last}")


@blueprint_cli.command("run")
@click.argument("name")
def blueprint_run(name: str):
    """Run a blueprint immediately (one-off execution)."""
    registry = BlueprintRegistry()
    definition = registry.match(name)
    if not definition:
        click.echo(f"Error: Unknown blueprint '{name}'")
        raise click.BadParameter(name)

    executor = _get_executor()
    result = executor.run(definition)
    click.echo(f"Blueprint '{name}' executed: {result.status}")
    if result.artifact_path:
        click.echo(f"  Artifact: {result.artifact_path}")
    if result.summary:
        click.echo(f"  Summary: {result.summary[:200]}")
    if result.error:
        click.echo(f"  Error: {result.error}")


@blueprint_cli.command("pause")
@click.argument("name")
def blueprint_pause(name: str):
    """Pause a scheduled blueprint job."""
    bridge = _get_bridge()
    if bridge.pause_job(name):
        click.echo(f"Blueprint '{name}' paused.")
    else:
        click.echo(f"Failed to pause '{name}'.")


@blueprint_cli.command("resume")
@click.argument("name")
def blueprint_resume(name: str):
    """Resume a paused blueprint job."""
    bridge = _get_bridge()
    if bridge.resume_job(name):
        click.echo(f"Blueprint '{name}' resumed.")
    else:
        click.echo(f"Failed to resume '{name}'.")


@blueprint_cli.command("delete")
@click.argument("name")
def blueprint_delete(name: str):
    """Delete a blueprint job."""
    bridge = _get_bridge()
    if bridge.delete_job(name):
        click.echo(f"Blueprint '{name}' deleted.")
    else:
        click.echo(f"Failed to delete '{name}'.")
