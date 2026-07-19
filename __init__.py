"""Delegation Kit — multi-model coding orchestrator for Hermes.

Routes coding work across local Claude Code, Codex, and Kimi CLI lanes
using the delegation-kit policy. Hermes acts as the lead/orchestrator;
the CLI tools execute in their respective lanes.

Lanes:
  - judgement: fable @ xhigh (default) · sol @ high (greenfield/budget)
               parallel fable+sol for critical decisions
  - senior:    opus @ high (security, taste, escalation)
  - builder:   kimi k3 @ max (default) · terra @ high (OpenAI-flavored,
               kimi quota fallback) · sonnet @ medium (ambiguous/critical)
  - clerk:     luna @ low (extraction, mapping) · glm @ high (volume)
  - reviewer:  sol @ high (routine correctness)

Escalation: builder → senior → judgement. Never retry the same lane twice.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

from tools.registry import registry


# ---------------------------------------------------------------------------
# Lane definitions
# ---------------------------------------------------------------------------

@dataclass
class Lane:
    """A delegation lane with its CLI command template."""
    name: str
    cli: str  # "claude", "codex", "kimi"
    model: str
    effort: str
    sandbox: Optional[str] = None  # for codex: read-only, workspace-write
    profile: Optional[str] = None  # for codex ephemeral profiles


LANES: Dict[str, Lane] = {
    # Judgement
    "judgement-fable": Lane("judgement-fable", "claude", "fable", "xhigh"),
    "judgement-sol": Lane("judgement-sol", "codex", "gpt-5.6-sol", "high"),
    # Senior
    "senior-opus": Lane("senior-opus", "claude", "opus", "high"),
    # Builder
    "builder-kimi": Lane("builder-kimi", "kimi", "k3", "max"),
    "builder-terra": Lane("builder-terra", "codex", "gpt-5.6-terra", "high"),
    "builder-sonnet": Lane("builder-sonnet", "claude", "sonnet", "medium"),
    # Clerk
    "clerk-luna": Lane("clerk-luna", "codex", "gpt-5.6-luna", "low", sandbox="read-only"),
    "clerk-glm": Lane("clerk-glm", "claude", "glm-5.2", "high"),
    # Reviewer
    "reviewer-sol": Lane("reviewer-sol", "codex", "gpt-5.6-sol", "high", sandbox="read-only"),
}

DEFAULT_BUILDER = "builder-kimi"
KIMI_QUOTA_FALLBACK = "builder-terra"


# ---------------------------------------------------------------------------
# CLI dispatch helpers
# ---------------------------------------------------------------------------

def _check_command(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def _write_brief(prompt: str, suffix: str = ".md") -> str:
    """Write prompt to a temp file for safe CLI passing."""
    fd, path = tempfile.mkstemp(suffix=suffix, prefix="delegation-brief-")
    with os.fdopen(fd, "w") as f:
        f.write(prompt)
    return path


def _run_claude(lane: Lane, prompt: str, cwd: str) -> Tuple[bool, str]:
    """Dispatch to Claude Code CLI."""
    if not _check_command("claude"):
        return False, "claude CLI not found"

    brief = _write_brief(prompt)
    cmd = [
        "claude",
        "--model", lane.model,
        "--effort", lane.effort,
        "--print",  # non-interactive
        f"$(cat '{brief}')",
    ]
    # Use shell expansion for safe prompt passing
    shell_cmd = f"claude --model {lane.model} --effort {lane.effort} --print \"$(cat '{brief}')\""

    try:
        result = subprocess.run(
            shell_cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=300,
        )
        os.unlink(brief)
        if result.returncode != 0:
            return False, f"claude exit {result.returncode}: {result.stderr[:500]}"
        return True, result.stdout
    except subprocess.TimeoutExpired:
        os.unlink(brief)
        return False, "claude timeout (300s)"
    except Exception as e:
        if os.path.exists(brief):
            os.unlink(brief)
        return False, f"claude error: {e}"


def _run_codex(lane: Lane, prompt: str, cwd: str) -> Tuple[bool, str]:
    """Dispatch to Codex CLI."""
    if not _check_command("codex"):
        return False, "codex CLI not found"

    brief = _write_brief(prompt)
    args = [
        "codex", "exec",
        "-m", lane.model,
        "-c", f"model_reasoning_effort={lane.effort}",
    ]
    if lane.sandbox:
        args.extend(["-s", lane.sandbox])
    if lane.profile:
        args.extend(["-p", lane.profile])
    args.extend(["-o", "/dev/stdout"])  # machine-readable stdout
    args.append(f"$(cat '{brief}')")

    shell_cmd = " ".join(args)

    try:
        result = subprocess.run(
            shell_cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=300,
        )
        os.unlink(brief)
        if result.returncode != 0:
            return False, f"codex exit {result.returncode}: {result.stderr[:500]}"
        return True, result.stdout
    except subprocess.TimeoutExpired:
        os.unlink(brief)
        return False, "codex timeout (300s)"
    except Exception as e:
        if os.path.exists(brief):
            os.unlink(brief)
        return False, f"codex error: {e}"


def _run_kimi(lane: Lane, prompt: str, cwd: str) -> Tuple[bool, str]:
    """Dispatch to Kimi via delegation-kimi wrapper."""
    if not _check_command("delegation-kimi"):
        # Fallback: try direct kimi CLI if available
        return _run_kimi_direct(lane, prompt, cwd)

    brief = _write_brief(prompt)
    shell_cmd = f"delegation-kimi exec --lane builder --effort {lane.effort} \"$(cat '{brief}')\""

    try:
        result = subprocess.run(
            shell_cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=300,
        )
        os.unlink(brief)
        if result.returncode == 75:
            return False, "kimi quota exhausted (exit 75) — use fallback lane"
        if result.returncode != 0:
            return False, f"kimi exit {result.returncode}: {result.stderr[:500]}"
        return True, result.stdout
    except subprocess.TimeoutExpired:
        os.unlink(brief)
        return False, "kimi timeout (300s)"
    except Exception as e:
        if os.path.exists(brief):
            os.unlink(brief)
        return False, f"kimi error: {e}"


def _run_kimi_direct(lane: Lane, prompt: str, cwd: str) -> Tuple[bool, str]:
    """Direct kimi CLI fallback (if delegation-kimi not installed)."""
    if not _check_command("kimi"):
        return False, "neither delegation-kimi nor kimi CLI found"
    brief = _write_brief(prompt)
    shell_cmd = f"kimi --model {lane.model} --effort {lane.effort} --print \"$(cat '{brief}')\""
    try:
        result = subprocess.run(
            shell_cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=300,
        )
        os.unlink(brief)
        if result.returncode != 0:
            return False, f"kimi exit {result.returncode}: {result.stderr[:500]}"
        return True, result.stdout
    except Exception as e:
        if os.path.exists(brief):
            os.unlink(brief)
        return False, f"kimi error: {e}"


# ---------------------------------------------------------------------------
# Lane selection logic
# ---------------------------------------------------------------------------

def _select_builder(task_description: str, security_critical: bool = False) -> str:
    """Select the appropriate builder lane."""
    if security_critical:
        return "builder-sonnet"
    # Check for ambiguity keywords
    ambiguous = any(w in task_description.lower() for w in [
        "ambiguous", "unclear", "figure out", "design", "architect",
        "multiple files", "cross-cutting", "refactor",
    ])
    if ambiguous:
        return "builder-sonnet"
    return DEFAULT_BUILDER


def _select_judgement(
    critical: bool = False,
    greenfield: bool = False,
    budget_conscious: bool = False,
) -> List[str]:
    """Select judgement lane(s). Returns list for parallel dispatch."""
    if critical:
        return ["judgement-fable", "judgement-sol"]  # parallel
    if greenfield or budget_conscious:
        return ["judgement-sol"]
    return ["judgement-fable"]


def _select_clerk(volume: bool = False) -> str:
    return "clerk-glm" if volume else "clerk-luna"


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def delegation_dispatch(
    task: str,
    lane: Optional[str] = None,
    cwd: Optional[str] = None,
    security_critical: bool = False,
    volume: bool = False,
    critical_decision: bool = False,
    greenfield: bool = False,
    budget_conscious: bool = False,
) -> str:
    """Dispatch a coding task to the appropriate delegation lane.

    Args:
        task: The task description / prompt
        lane: Force a specific lane (overrides auto-selection)
        cwd: Working directory for the task (default: current)
        security_critical: Route to senior/secure lanes
        volume: Use high-volume cheap lanes
        critical_decision: Use parallel judgement
        greenfield: Greenfield project (use sol for judgement)
        budget_conscious: Prefer cheaper judgement
    """
    cwd = cwd or os.getcwd()

    # Auto-select lane if not forced
    if not lane:
        if critical_decision:
            lanes = _select_judgement(critical=True, greenfield=greenfield, budget_conscious=budget_conscious)
        elif "review" in task.lower() or "audit" in task.lower():
            if security_critical:
                lanes = ["senior-opus"]
            else:
                lanes = ["reviewer-sol"]
        elif "extract" in task.lower() or "map" in task.lower() or "inventory" in task.lower():
            lanes = [_select_clerk(volume)]
        elif "plan" in task.lower() or "architect" in task.lower() or "decide" in task.lower():
            lanes = _select_judgement(greenfield=greenfield, budget_conscious=budget_conscious)
        else:
            lanes = [_select_builder(task, security_critical)]
    else:
        lanes = [lane]

    # Dispatch to selected lane(s)
    results: Dict[str, Dict[str, Any]] = {}

    for lane_name in lanes:
        if lane_name not in LANES:
            results[lane_name] = {"success": False, "error": f"unknown lane: {lane_name}"}
            continue

        lane_obj = LANES[lane_name]

        if lane_obj.cli == "claude":
            success, output = _run_claude(lane_obj, task, cwd)
        elif lane_obj.cli == "codex":
            success, output = _run_codex(lane_obj, task, cwd)
        elif lane_obj.cli == "kimi":
            success, output = _run_kimi(lane_obj, task, cwd)
        else:
            success, output = False, f"unknown cli: {lane_obj.cli}"

        results[lane_name] = {
            "success": success,
            "output": output[:4000] if success else None,
            "error": None if success else output,
            "model": lane_obj.model,
            "effort": lane_obj.effort,
        }

        # Handle kimi quota fallback
        if not success and lane_obj.cli == "kimi" and "quota exhausted" in output:
            fallback = LANES.get(KIMI_QUOTA_FALLBACK)
            if fallback:
                fb_success, fb_output = _run_codex(fallback, task, cwd)
                results[f"{lane_name}->fallback-{KIMI_QUOTA_FALLBACK}"] = {
                    "success": fb_success,
                    "output": fb_output[:4000] if fb_success else None,
                    "error": None if fb_success else fb_output,
                    "model": fallback.model,
                    "effort": fallback.effort,
                    "note": "kimi quota fallback",
                }

    return json.dumps({
        "lanes_dispatched": lanes,
        "results": results,
        "parallel_judgement": len(lanes) > 1,
    }, indent=2)


def delegation_escalate(
    original_lane: str,
    task: str,
    failure_reason: str,
    cwd: Optional[str] = None,
) -> str:
    """Escalate a failed task to the next lane up.

    Ladder: builder → senior → judgement
    """
    cwd = cwd or os.getcwd()

    escalation_map = {
        "builder-kimi": "senior-opus",
        "builder-terra": "senior-opus",
        "builder-sonnet": "senior-opus",
        "senior-opus": "judgement-fable",
        "clerk-luna": "builder-kimi",
        "clerk-glm": "builder-kimi",
        "reviewer-sol": "senior-opus",
    }

    next_lane = escalation_map.get(original_lane)
    if not next_lane:
        return json.dumps({
            "success": False,
            "error": f"no escalation path from {original_lane}",
            "original_failure": failure_reason,
        })

    # Never retry the same lane twice — escalate directly
    result = delegation_dispatch(
        task=task,
        lane=next_lane,
        cwd=cwd,
    )

    return json.dumps({
        "escalated_from": original_lane,
        "escalated_to": next_lane,
        "failure_reason": failure_reason,
        "result": json.loads(result),
    }, indent=2)


def delegation_status() -> str:
    """Check availability of all delegation lanes."""
    status = {}
    for name, lane in LANES.items():
        if lane.cli == "claude":
            available = _check_command("claude")
        elif lane.cli == "codex":
            available = _check_command("codex")
        elif lane.cli == "kimi":
            available = _check_command("delegation-kimi") or _check_command("kimi")
        else:
            available = False

        status[name] = {
            "available": available,
            "cli": lane.cli,
            "model": lane.model,
            "effort": lane.effort,
        }

    return json.dumps(status, indent=2)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def _register_delegation_tools():
    """Register delegation tools with Hermes."""

    def check_delegation_available() -> bool:
        return _check_command("claude") or _check_command("codex")

    registry.register(
        name="delegation_dispatch",
        toolset="delegation",
        schema={
            "name": "delegation_dispatch",
            "description": (
                "Dispatch a coding task to the appropriate delegation lane. "
                "Auto-selects lane based on task type: judgement for planning/architecture, "
                "senior for security/taste, builder for implementation (default: kimi k3), "
                "clerk for extraction/mapping, reviewer for routine correctness. "
                "Use lane parameter to force a specific lane."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The task description / prompt to dispatch",
                    },
                    "lane": {
                        "type": "string",
                        "description": "Force a specific lane (e.g. builder-kimi, judgement-fable, senior-opus)",
                        "enum": list(LANES.keys()),
                    },
                    "cwd": {
                        "type": "string",
                        "description": "Working directory for the task",
                    },
                    "security_critical": {
                        "type": "boolean",
                        "description": "Route to security-appropriate lanes",
                        "default": False,
                    },
                    "volume": {
                        "type": "boolean",
                        "description": "Use high-volume cheap lanes (glm for clerk)",
                        "default": False,
                    },
                    "critical_decision": {
                        "type": "boolean",
                        "description": "Use parallel judgement (fable + sol)",
                        "default": False,
                    },
                    "greenfield": {
                        "type": "boolean",
                        "description": "Greenfield project — use sol for judgement",
                        "default": False,
                    },
                    "budget_conscious": {
                        "type": "boolean",
                        "description": "Prefer cheaper judgement options",
                        "default": False,
                    },
                },
                "required": ["task"],
            },
        },
        handler=lambda args, **kw: delegation_dispatch(
            task=args.get("task", ""),
            lane=args.get("lane"),
            cwd=args.get("cwd"),
            security_critical=args.get("security_critical", False),
            volume=args.get("volume", False),
            critical_decision=args.get("critical_decision", False),
            greenfield=args.get("greenfield", False),
            budget_conscious=args.get("budget_conscious", False),
        ),
        check_fn=check_delegation_available,
    )

    registry.register(
        name="delegation_escalate",
        toolset="delegation",
        schema={
            "name": "delegation_escalate",
            "description": (
                "Escalate a failed task to the next lane up. "
                "Never retry the same lane twice. "
                "Ladder: builder → senior → judgement."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "original_lane": {
                        "type": "string",
                        "description": "The lane that failed",
                    },
                    "task": {
                        "type": "string",
                        "description": "The original task",
                    },
                    "failure_reason": {
                        "type": "string",
                        "description": "Why the original lane failed",
                    },
                    "cwd": {
                        "type": "string",
                        "description": "Working directory",
                    },
                },
                "required": ["original_lane", "task", "failure_reason"],
            },
        },
        handler=lambda args, **kw: delegation_escalate(
            original_lane=args.get("original_lane", ""),
            task=args.get("task", ""),
            failure_reason=args.get("failure_reason", ""),
            cwd=args.get("cwd"),
        ),
        check_fn=check_delegation_available,
    )

    registry.register(
        name="delegation_status",
        toolset="delegation",
        schema={
            "name": "delegation_status",
            "description": "Check availability of all delegation lanes (claude, codex, kimi CLIs).",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
        handler=lambda args, **kw: delegation_status(),
        check_fn=lambda: True,  # always available
    )


_register_delegation_tools()
