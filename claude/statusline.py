#!/usr/bin/env python3
"""
Statusline script for Claude Code.

Reads JSON from stdin (provided by Claude Code) and renders a compact statusline.
Based on oh-my-claudecode HUD, without the [OMC] label.

Usage in ~/.claude/settings.json:
  {
    "statusLine": {
      "type": "command",
      "command": "python3 ~/dotfiles/claude/statusline.py"
    }
  }
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time

# ---------------------------------------------------------------------------
# ANSI colors
# ---------------------------------------------------------------------------
RESET = "\033[0m"
DIM = "\033[2m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"


def dim(text: str) -> str:
    return f"{DIM}{text}{RESET}"


def bold(text: str) -> str:
    return f"{BOLD}{text}{RESET}"


def cyan(text: str) -> str:
    return f"{CYAN}{text}{RESET}"


def green(text: str) -> str:
    return f"{GREEN}{text}{RESET}"


def yellow(text: str) -> str:
    return f"{YELLOW}{text}{RESET}"


def red(text: str) -> str:
    return f"{RED}{text}{RESET}"


def magenta(text: str) -> str:
    return f"{MAGENTA}{text}{RESET}"


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
CONTEXT_WARNING = 70
CONTEXT_COMPACT_SUGGESTION = 80
CONTEXT_CRITICAL = 85

# ---------------------------------------------------------------------------
# stdin helpers
# ---------------------------------------------------------------------------


def read_stdin() -> dict | None:
    if sys.stdin.isatty():
        return None
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return None
        return json.loads(raw)
    except Exception:
        return None


def get_context_percent(stdin: dict) -> int:
    native = (stdin.get("context_window") or {}).get("used_percentage")
    if isinstance(native, (int, float)):
        return min(100, max(0, round(native)))
    size = (stdin.get("context_window") or {}).get("context_window_size", 0)
    if not size or size <= 0:
        return 0
    usage = (stdin.get("context_window") or {}).get("current_usage") or {}
    total = (
        (usage.get("input_tokens") or 0)
        + (usage.get("cache_creation_input_tokens") or 0)
        + (usage.get("cache_read_input_tokens") or 0)
    )
    return min(100, round(total / size * 100))


def get_model_name(stdin: dict) -> str:
    model = stdin.get("model") or {}
    return model.get("display_name") or model.get("id") or "Unknown"


# ---------------------------------------------------------------------------
# Render helpers
# ---------------------------------------------------------------------------


def format_model_name(model_id: str) -> str:
    low = model_id.lower()
    if "opus" in low:
        return "Opus"
    if "sonnet" in low:
        return "Sonnet"
    if "haiku" in low:
        return "Haiku"
    return model_id[:17] + "..." if len(model_id) > 20 else model_id


def render_model(model_id: str) -> str | None:
    name = format_model_name(model_id)
    if not name:
        return None
    return f"{dim('model:')}{cyan(name)}"


def render_cwd(cwd: str) -> str | None:
    if not cwd:
        return None
    home = os.path.expanduser("~")
    display = "~" + cwd[len(home) :] if cwd.startswith(home) else cwd
    return dim(display)


def _run_git(cwd: str, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "--no-optional-locks", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=1,
        )
        out = result.stdout.strip()
        return out if out else None
    except Exception:
        return None


def render_git_repo(cwd: str) -> str | None:
    url = _run_git(cwd, "remote", "get-url", "origin")
    if not url:
        return None
    import re

    m = re.search(r"/([^/]+?)(?:\.git)?$", url) or re.search(
        r":([^/]+?)(?:\.git)?$", url
    )
    name = m.group(1).removesuffix(".git") if m else None
    if not name:
        return None
    return f"{dim('repo:')}{cyan(name)}"


def render_git_branch(cwd: str) -> str | None:
    branch = _run_git(cwd, "branch", "--show-current")
    if not branch:
        return None
    return f"{dim('branch:')}{cyan(branch)}"


def render_context(percent: int) -> str:
    safe = min(100, max(0, round(percent)))
    if safe >= CONTEXT_CRITICAL:
        color = RED
        suffix = " CRITICAL"
    elif safe >= CONTEXT_COMPACT_SUGGESTION:
        color = YELLOW
        suffix = " COMPRESS?"
    elif safe >= CONTEXT_WARNING:
        color = YELLOW
        suffix = ""
    else:
        color = GREEN
        suffix = ""
    return f"ctx:{color}{safe}%{suffix}{RESET}"


def render_context_bar(percent: int, bar_width: int = 10) -> str:
    safe = min(100, max(0, round(percent)))
    filled = round(safe / 100 * bar_width)
    empty = bar_width - filled
    if safe >= CONTEXT_CRITICAL:
        color = RED
    elif safe >= CONTEXT_WARNING:
        color = YELLOW
    else:
        color = GREEN
    bar = f"{color}{'█' * filled}{DIM}{'░' * empty}{RESET}"
    return f"ctx:[{bar}]{color}{safe}%{RESET}"


def render_session(duration_minutes: int, health: str) -> str:
    if health == "critical":
        color = RED
    elif health == "warning":
        color = YELLOW
    else:
        color = GREEN
    return f"session:{color}{duration_minutes}m{RESET}"


def format_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


def render_session_analytics(stdin: dict, duration_minutes: int) -> str | None:
    usage = (stdin.get("context_window") or {}).get("current_usage") or {}
    input_tokens = usage.get("input_tokens") or 0
    cache_creation = usage.get("cache_creation_input_tokens") or 0
    cache_read = usage.get("cache_read_input_tokens") or 0
    total_tokens = input_tokens + cache_creation + cache_read
    if total_tokens == 0:
        return None

    total_input_for_cache = input_tokens + cache_creation
    cache_hit_rate = (
        (cache_read / (total_input_for_cache + cache_read) * 100)
        if (total_input_for_cache + cache_read) > 0
        else 0
    )

    parts = [
        f"tok:{format_tokens(total_tokens)}",
        f"cache:{cache_hit_rate:.0f}%",
    ]
    return " | ".join(parts)


# ---------------------------------------------------------------------------
# Nyan Cat animation
# ---------------------------------------------------------------------------

# Rainbow colors (ANSI 256-color for orange, rest are standard bright)
RAINBOW = [
    "\033[91m",        # bright red
    "\033[38;5;208m",  # orange
    "\033[93m",        # bright yellow
    "\033[92m",        # bright green
    "\033[96m",        # bright cyan
    "\033[95m",        # bright magenta
]

NYAN_WIDTH = 14   # walking area width
NYAN_PERIOD = 8.0  # seconds per full bounce cycle
TRAIL_LEN = 8     # rainbow trail length
STARS = ["✧", "✦", "⋆", "·"]


def render_nyan_cat() -> str:
    """Render a Nyan Cat with a flowing rainbow trail."""
    t = time.time()

    # --- position (ping-pong) ---
    phase = (t % NYAN_PERIOD) / NYAN_PERIOD
    if phase < 0.5:
        pos = int(phase * 2 * NYAN_WIDTH)
        going_right = True
    else:
        pos = NYAN_WIDTH - int((phase - 0.5) * 2 * NYAN_WIDTH)
        going_right = False
    pos = max(0, min(NYAN_WIDTH, pos))

    # --- rainbow trail (colors flow over time) ---
    shift = int(t * 6)
    trail = ""
    for i in range(TRAIL_LEN):
        ci = (i + shift) % len(RAINBOW)
        trail += f"{RAINBOW[ci]}━{RESET}"

    # --- cat face ---
    blink = int(t * 3) % 8 == 7
    eyes = "- -" if blink else "^.^"
    cat = f"{YELLOW}[{RESET}={eyes}={YELLOW}]{RESET}"

    # --- twinkling stars ---
    s1 = STARS[int(t * 3) % len(STARS)]
    s2 = STARS[int(t * 2 + 1) % len(STARS)]

    if going_right:
        return " " * pos + f"{trail}{cat} {s1}"
    else:
        return " " * pos + f"{s2} {cat}{trail}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

MAX_OUTPUT_LINES = 4


def main() -> None:
    stdin = read_stdin()
    if not stdin:
        return

    cwd = stdin.get("cwd") or os.getcwd()
    model_name = get_model_name(stdin)
    context_percent = get_context_percent(stdin)

    # --- Line 1: git info ---
    git_elements: list[str] = []
    cwd_el = render_cwd(cwd)
    if cwd_el:
        git_elements.append(cwd_el)
    repo_el = render_git_repo(cwd)
    if repo_el:
        git_elements.append(repo_el)
    branch_el = render_git_branch(cwd)
    if branch_el:
        git_elements.append(branch_el)
    model_el = render_model(model_name)
    if model_el:
        git_elements.append(model_el)

    # --- Line 2: HUD header ---
    elements: list[str] = []

    # Session health
    usage = (stdin.get("context_window") or {}).get("current_usage") or {}
    duration_minutes = 0
    health = "healthy"
    if context_percent > 85:
        health = "critical"
    elif context_percent > 70:
        health = "warning"

    session_el = render_session(duration_minutes, health)
    elements.append(session_el)

    # Session analytics (tokens, cache)
    analytics = render_session_analytics(stdin, duration_minutes)
    if analytics:
        elements.append(analytics)

    # Context bar
    ctx_el = render_context_bar(context_percent)
    elements.append(ctx_el)

    # --- Line 3: nyan cat ---
    cat_line = render_nyan_cat()

    # --- Compose output ---
    output_lines: list[str] = []
    if git_elements:
        output_lines.append(dim(" | ").join(git_elements))
    output_lines.append(dim(" | ").join(elements))
    output_lines.append(cat_line)

    # Limit output lines
    if len(output_lines) > MAX_OUTPUT_LINES:
        output_lines = output_lines[: MAX_OUTPUT_LINES - 1] + [
            f"... (+{len(output_lines) - MAX_OUTPUT_LINES + 1} lines)"
        ]

    # Replace spaces with non-breaking spaces for terminal alignment
    formatted = "\n".join(output_lines).replace(" ", "\u00a0")
    print(formatted)


if __name__ == "__main__":
    main()
