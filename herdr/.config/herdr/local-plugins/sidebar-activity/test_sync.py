import datetime as dt
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import sync


class ConversationTimesTests(unittest.TestCase):
    def test_unidentified_sessions_and_ambiguous_claude_sessions_stay_empty(self):
        with tempfile.TemporaryDirectory() as temporary:
            reader = sync.ConversationTimes()
            reader.claude = Path(temporary)
            self.assertIsNone(reader.read(None))
            self.assertIsNone(reader.read({"agent": "codex", "kind": "id", "value": "../other"}))
            for project in ("first", "second"):
                path = reader.claude / "projects" / project / "same-id.jsonl"
                path.parent.mkdir(parents=True)
                path.write_text('{}\n')
            self.assertIsNone(reader.read({"agent": "claude", "kind": "id", "value": "same-id"}))

    def test_codex_date_comes_from_messages_in_the_exact_thread(self):
        with tempfile.TemporaryDirectory() as temporary:
            reader = sync.ConversationTimes()
            reader.codex = Path(temporary)
            with sqlite3.connect(str(reader.codex / "thread_history_1.sqlite")) as connection:
                connection.execute("CREATE TABLE thread_items(thread_id, item_type, created_at_ms)")
                connection.executemany("INSERT INTO thread_items VALUES(?, ?, ?)", [
                    ("selected", "userMessage", 1000), ("selected", "agentMessage", 2000),
                    ("selected", "toolCall", 8000), ("another", "agentMessage", 9000),
                ])
            actual = reader.read({"agent": "codex", "kind": "id", "value": "selected"})
            self.assertEqual(actual, dt.datetime.fromtimestamp(2, dt.timezone.utc))

    def test_claude_metadata_and_other_session_messages_do_not_advance_date(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "session.jsonl"
            events = [
                {"type": "assistant", "sessionId": "selected", "message": {"role": "assistant"},
                 "timestamp": "2026-11-09T00:00:00Z"},
                {"type": "progress", "timestamp": "2026-11-09T01:00:00Z"},
                {"type": "user", "message": {"role": "user"}, "isMeta": True,
                 "timestamp": "2026-11-09T02:00:00Z"},
                {"type": "assistant", "sessionId": "other", "message": {"role": "assistant"},
                 "timestamp": "2026-11-09T03:00:00Z"},
            ]
            path.write_text('\n'.join(json.dumps(event) for event in events))
            reader = sync.ConversationTimes()
            self.assertEqual(reader.jsonl(path, "claude", "selected"),
                             sync.timestamp("2026-11-09T00:00:00Z"))

    def test_claude_tool_traffic_and_reasoning_do_not_advance_date(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "session.jsonl"
            events = [
                {"type": "user", "message": {"role": "user", "content": "question"},
                 "timestamp": "2026-11-09T00:00:00Z"},
                {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text"}]},
                 "timestamp": "2026-11-09T01:00:00Z"},
                {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use"}]},
                 "timestamp": "2026-11-09T02:00:00Z"},
                {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result"}]},
                 "timestamp": "2026-11-09T03:00:00Z"},
                {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "thinking"}]},
                 "timestamp": "2026-11-09T04:00:00Z"},
            ]
            path.write_text('\n'.join(json.dumps(event) for event in events))
            reader = sync.ConversationTimes()
            self.assertEqual(reader.jsonl(path, "claude", None),
                             sync.timestamp("2026-11-09T01:00:00Z"))

    def test_lookup_cut_short_is_unavailable_rather_than_empty(self):
        with tempfile.TemporaryDirectory() as temporary:
            database = Path(temporary) / "thread_history_1.sqlite"
            with sqlite3.connect(str(database)) as connection:
                connection.execute("CREATE TABLE thread_items(thread_id, item_type, created_at_ms)")
            reference = {"agent": "codex", "kind": "id", "value": "selected"}

            out_of_time = sync.ConversationTimes()
            out_of_time.codex = Path(temporary)
            out_of_time.deadline = 0
            self.assertIs(out_of_time.read(reference), sync.UNAVAILABLE)

            transcript = Path(temporary) / "session.jsonl"
            transcript.write_text('{}\n')
            self.assertIs(out_of_time.jsonl(transcript, "claude", None), sync.UNAVAILABLE)

            locked = sync.ConversationTimes()
            locked.codex = Path(temporary)
            writer = sqlite3.connect(str(database), isolation_level=None)
            try:
                writer.execute("BEGIN EXCLUSIVE")
                self.assertIs(locked.read(reference), sync.UNAVAILABLE)
            finally:
                writer.close()

            # An older database version without the table is "no conversation", not a failure.
            with sqlite3.connect(str(database)) as connection:
                connection.execute("DROP TABLE thread_items")
            older = sync.ConversationTimes()
            older.codex = Path(temporary)
            self.assertIsNone(older.read(reference))

    def test_sync_keeps_the_shown_date_when_the_lookup_is_unavailable(self):
        agent = {"terminal_id": "term1", "pane_id": "w1:p1", "agent": "codex",
                 "agent_session": {"agent": "codex", "kind": "id", "value": "selected"},
                 "tokens": {sync.TOKEN: "old date"}}
        with patch.object(sync, "agents", return_value={"term1": agent}), \
                patch.object(sync.ConversationTimes, "read", return_value=sync.UNAVAILABLE), \
                patch.object(sync, "rpc") as rpc:
            sync.sync()
        rpc.assert_not_called()

    def test_sync_clears_unknown_dates_and_skips_replaced_agents(self):
        unknown = {"terminal_id": "term1", "pane_id": "w1:p1", "agent": "codex",
                   "tokens": {sync.TOKEN: "old date", "keep": "untouched"}}
        replaced = dict(unknown, terminal_id="term2", pane_id="w1:p2")
        before = {"term1": unknown, "term2": replaced}
        after = dict(before, term2=dict(replaced, agent="claude"))
        with patch.object(sync, "agents", side_effect=[before, after]), \
                patch.object(sync, "rpc") as rpc, \
                patch.dict(sync.os.environ, {"HERDR_PLUGIN_ID": "sidebar-activity"}):
            sync.sync()
        rpc.assert_called_once_with("pane.report_metadata", {
            "pane_id": "w1:p1", "source": "plugin:sidebar-activity",
            "tokens": {sync.TOKEN: None},
        })
        self.assertEqual(unknown["tokens"]["keep"], "untouched")

    def test_sync_does_not_borrow_a_reference_from_another_agent_kind(self):
        agent = {"terminal_id": "term1", "pane_id": "w1:p1", "agent": "codex",
                 "agent_session": {"agent": "claude", "kind": "id", "value": "old-session"},
                 "tokens": {sync.TOKEN: "old date"}}
        with patch.object(sync, "agents", return_value={"term1": agent}), \
                patch.object(sync.ConversationTimes, "read") as read, \
                patch.object(sync, "rpc") as rpc, \
                patch.dict(sync.os.environ, {"HERDR_PLUGIN_ID": "sidebar-activity"}):
            sync.sync()
        read.assert_not_called()
        self.assertIsNone(rpc.call_args[0][1]["tokens"][sync.TOKEN])


if __name__ == "__main__":
    unittest.main()
