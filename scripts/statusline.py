#!/usr/bin/env python3
"""Claude Code statusline. Reads session JSON from stdin, prints two lines.

Line 1: path · repo/branch · worktree · model · modes
Line 2: ctx bar · rate limits · session time · diff · PR
Optional segments (worktree, rate limits, PR, ...) are omitted when absent.
"""
import json
import os
import subprocess
import sys

RESET, DIM = "\033[0m", "\033[2m"
GREEN, YELLOW, RED, CYAN, MAGENTA, BLUE, ORANGE = (
    "\033[32m", "\033[33m", "\033[31m", "\033[36m", "\033[35m", "\033[34m", "\033[38;5;208m",
)


def paint(color, text):
    return f"{color}{text}{RESET}"


def label(name, value, color=CYAN):
    return f"{DIM}{name}:{RESET}{paint(color, value)}"


def level_color(pct, warn, crit):
    return RED if pct >= crit else YELLOW if pct >= warn else GREEN


def git_branch(cwd):
    """Return (branch, dirty) from one git call, or (None, False)."""
    try:
        out = subprocess.run(
            ["git", "--no-optional-locks", "status", "--porcelain=v2", "--branch"],
            cwd=cwd, capture_output=True, text=True, timeout=1,
        ).stdout
    except Exception:
        return None, False
    branch, dirty = None, False
    for line in out.splitlines():
        if line.startswith("# branch.head "):
            branch = line.split(" ", 2)[2]
        elif not line.startswith("#"):
            dirty = True
    return (None if branch == "(detached)" else branch), dirty


def fmt_duration(ms):
    m = ms // 60_000
    return f"{m // 60}h{m % 60:02d}m" if m >= 60 else f"{m}m"


def line1(d):
    cwd = d.get("cwd") or os.getcwd()
    home = os.path.expanduser("~")
    parts = [paint(DIM, "~" + cwd[len(home):] if cwd.startswith(home) else cwd)]

    repo = (d.get("workspace") or {}).get("repo") or {}
    if repo.get("name"):
        parts.append(label("repo", repo["name"]))
    branch, dirty = git_branch(cwd)
    if branch:
        parts.append(label("branch", branch) + (paint(YELLOW, "*") if dirty else ""))

    wt = (d.get("workspace") or {}).get("git_worktree") or (d.get("worktree") or {}).get("name")
    if wt:
        parts.append(label("wt", wt, ORANGE))

    model = d.get("model") or {}
    parts.append(label("model", model.get("display_name") or model.get("id") or "?"))
    if (d.get("effort") or {}).get("level"):
        parts.append(label("effort", d["effort"]["level"], MAGENTA))
    if d.get("fast_mode"):
        parts.append(paint(MAGENTA, "fast"))
    if (d.get("thinking") or {}).get("enabled") is False:
        parts.append(paint(DIM, "no-think"))
    if (d.get("vim") or {}).get("mode"):
        parts.append(label("vim", d["vim"]["mode"], MAGENTA))
    return parts


def line2(d):
    ctx = d.get("context_window") or {}
    pct = int(ctx.get("used_percentage") or 0)
    color = level_color(pct, 70, 85)
    filled = round(pct / 10)
    bar = paint(color, "█" * filled) + paint(DIM, "░" * (10 - filled))
    parts = [f"{DIM}ctx{RESET} {bar} {paint(color, f'{pct}%')}"]

    rl = d.get("rate_limits") or {}
    rl_parts = []
    for key, name in (("five_hour", "5h"), ("seven_day", "7d")):
        used = (rl.get(key) or {}).get("used_percentage")
        if used is not None:
            rl_parts.append(label(name, f"{used:.0f}%", level_color(used, 75, 90)))
    if rl_parts:
        parts.append(" ".join(rl_parts))

    cost = d.get("cost") or {}
    session = fmt_duration(cost.get("total_duration_ms") or 0)
    if d.get("session_name"):
        session = f"{d['session_name']} {session}"
    parts.append(paint(DIM, session))

    added, removed = cost.get("total_lines_added") or 0, cost.get("total_lines_removed") or 0
    if added or removed:
        parts.append(paint(GREEN, f"+{added}") + paint(RED, f"-{removed}"))

    pr = d.get("pr") or {}
    if pr.get("number"):
        seg = paint(BLUE, f"#{pr['number']}")
        if pr.get("review_state"):
            seg += " " + paint(DIM, pr["review_state"])
        parts.append(seg)
    return parts


def main():
    try:
        d = json.load(sys.stdin)
    except Exception:
        return
    out = "\n".join("  ".join(parts) for parts in (line1(d), line2(d)))
    print(out.replace(" ", "\u00a0"))


if __name__ == "__main__":
    main()
