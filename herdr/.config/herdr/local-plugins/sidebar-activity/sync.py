"""Publish verified conversation times without changing agent identity or order."""

import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import sqlite3
import time

TOKEN = "sidebar_last_active"
MAX_BYTES = 1024 * 1024
# A lookup that could not finish: the time budget ran out or a database was
# locked. None means something else, that the conversation has no verifiable time.
UNAVAILABLE = object()
# Claude content blocks that are not conversation: tool traffic and reasoning.
SILENT_BLOCKS = {"tool_use", "tool_result", "thinking", "redacted_thinking"}


def rpc(method, params):
    request_id = str(time.monotonic_ns())
    with socket.socket(socket.AF_UNIX) as stream:
        stream.settimeout(2)
        stream.connect(os.environ["HERDR_SOCKET_PATH"])
        stream.sendall(json.dumps({"id": request_id, "method": method,
                                   "params": params}).encode() + b"\n")
        with stream.makefile("rb") as response:
            raw = response.readline(8 * MAX_BYTES + 1)
    if len(raw) > 8 * MAX_BYTES:
        raise RuntimeError("Herdr response exceeded the size limit")
    result = json.loads(raw)
    if result.get("id") != request_id or "error" in result:
        raise RuntimeError("Herdr request failed: " + str(result.get("error")))
    return result["result"]


def agents():
    snapshot = rpc("session.snapshot", {})["snapshot"]
    panes = {p["terminal_id"]: p for p in snapshot["panes"]}
    result = {}
    for agent in snapshot["agents"]:
        agent = dict(agent)
        pane = panes.get(agent["terminal_id"], {})
        agent["agent_session"] = agent.get("agent_session") or pane.get("agent_session")
        result[agent["terminal_id"]] = agent
    return result


def identity(agent):
    reference = agent.get("agent_session") or {}
    return (agent["terminal_id"], agent.get("agent"), reference.get("agent"),
            reference.get("kind"), reference.get("value"))


def spoken(message):
    """False when every content block of a Claude message is tool traffic or reasoning."""
    content = message.get("content")
    if not isinstance(content, list) or not content:
        return True
    return any(not isinstance(block, dict) or block.get("type") not in SILENT_BLOCKS
               for block in content)


def timestamp(value):
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None else None
    except (AttributeError, TypeError, ValueError):
        return None


class ConversationTimes:
    def __init__(self):
        self.codex = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
        self.claude = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
        self.deadline = time.monotonic() + 0.8

    def databases(self, prefix):
        versions = []
        for path in self.codex.glob(prefix + "_*.sqlite"):
            version = path.stem[len(prefix) + 1:]
            if version.isdigit():
                versions.append((int(version), path))
        return [path for _, path in sorted(versions, reverse=True)[:8]]

    def query(self, path, sql, session_id):
        if time.monotonic() >= self.deadline:
            return UNAVAILABLE
        try:
            # Without uri=True the "file:...?mode=ro" string is only read as a URI
            # on SQLite builds compiled with URI filenames enabled.
            connection = sqlite3.connect(path.as_uri() + "?mode=ro", timeout=0.05, uri=True)
            try:
                connection.set_progress_handler(
                    lambda: time.monotonic() >= self.deadline, 1000)
                row = connection.execute(sql, (session_id,)).fetchone()
                return row[0] if row else None
            finally:
                connection.close()
        except sqlite3.Error as error:
            # An older database version without the table is a normal "no data" answer.
            # Only a lock or an exhausted time budget leaves the answer unknown.
            if time.monotonic() >= self.deadline or "locked" in str(error):
                return UNAVAILABLE
            return None

    def jsonl(self, path, provider, session_id):
        try:
            with path.open("rb") as stream:
                start = max(0, stream.seek(0, 2) - MAX_BYTES)
                stream.seek(start)
                if start:
                    stream.readline(MAX_BYTES)
                lines = stream.read(MAX_BYTES).splitlines()[-2000:]
        except OSError:
            return None
        latest = None
        for line in reversed(lines):
            if time.monotonic() >= self.deadline:
                return UNAVAILABLE
            if len(line) > 262144:
                continue
            try:
                event = json.loads(line)
                kind = event.get("type")
                payload = event.get("payload") or {}
                if provider == "claude":
                    message = event.get("message") or {}
                    relevant = (kind in ("user", "assistant")
                                and message.get("role") == kind
                                and not event.get("isMeta")
                                and (not session_id or event.get("sessionId", session_id) == session_id)
                                and spoken(message))
                else:
                    relevant = ((kind == "response_item" and payload.get("type") == "message"
                                 and payload.get("role") in ("user", "assistant"))
                                or (kind == "event_msg"
                                    and payload.get("type") in ("user_message", "agent_message")))
                at = timestamp(event.get("timestamp")) if relevant else None
                if at is not None:
                    latest = at if latest is None else max(latest, at)
            except (ValueError, TypeError, AttributeError):
                continue
        return latest

    def read(self, reference):
        reference = reference or {}
        provider, kind, value = (reference.get(key) for key in ("agent", "kind", "value"))
        if provider not in ("codex", "claude") or not isinstance(value, str):
            return None
        if kind == "path":
            path = Path(value)
            return self.jsonl(path, provider, None) if path.is_absolute() else None
        if kind != "id" or re.fullmatch(r"[A-Za-z0-9_-]{1,128}", value) is None:
            return None
        if provider == "claude":
            matches = list((self.claude / "projects").glob("*/" + value + ".jsonl"))
            return self.jsonl(matches[0], provider, value) if len(matches) == 1 else None
        latest = None
        for path in self.databases("thread_history"):
            millis = self.query(path, "SELECT MAX(created_at_ms) FROM thread_items "
                                "WHERE thread_id=? AND item_type IN ('userMessage','agentMessage')", value)
            if millis is UNAVAILABLE:
                return UNAVAILABLE
            if isinstance(millis, (int, float)):
                try:
                    at = dt.datetime.fromtimestamp(millis / 1000, dt.timezone.utc)
                    latest = at if latest is None else max(latest, at)
                except (OverflowError, OSError, ValueError):
                    pass
        if latest is not None:
            return latest
        for path in self.databases("state"):
            rollout = self.query(path, "SELECT rollout_path FROM threads WHERE id=? LIMIT 1", value)
            if rollout is UNAVAILABLE:
                return UNAVAILABLE
            if isinstance(rollout, str) and Path(rollout).is_absolute():
                return self.jsonl(Path(rollout), provider, value)
        return None


def sync():
    before = agents()
    reader = ConversationTimes()
    resolved, dates = {}, {}
    for terminal, agent in before.items():
        key = identity(agent)[1:]
        if key not in resolved:
            resolved[key] = reader.read(agent.get("agent_session")) if key[0] == key[1] else None
        at = resolved[key]
        if at is UNAVAILABLE:
            # Leave the shown value alone. Clearing it would make a verified time
            # disappear and come back whenever a lookup is cut short.
            continue
        dates[terminal] = at.astimezone().strftime("%Y-%m-%d %H:%M") if at else None
    # Panes can move or start another agent while their conversation files are read.
    for terminal, current in agents().items():
        old = before.get(terminal)
        if terminal not in dates or old is None or identity(old) != identity(current):
            continue
        value = dates[terminal]
        if current.get("tokens", {}).get(TOKEN) != value:
            try:
                rpc("pane.report_metadata", {"pane_id": current["pane_id"],
                                            "source": "plugin:" + os.environ["HERDR_PLUGIN_ID"],
                                            "tokens": {TOKEN: value}})
            except RuntimeError:
                # The pane can close between the snapshot and this call. The
                # remaining panes still need their update.
                continue


def main():
    state = Path(os.environ["HERDR_PLUGIN_STATE_DIR"])
    state.mkdir(parents=True, exist_ok=True)
    session = hashlib.sha256(os.environ["HERDR_SOCKET_PATH"].encode()).hexdigest()[:16]
    # Each event leaves a request flag and then waits for the lock. A sync that
    # starts after the flag was set already covers that event, so the waiter
    # skips. Exiting without waiting would drop events that arrive after a
    # running sync has taken its snapshot.
    pending = state / (session + ".pending")
    pending.touch()
    with (state / (session + ".lock")).open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if not pending.exists():
            return
        pending.unlink()
        sync()


if __name__ == "__main__":
    main()
