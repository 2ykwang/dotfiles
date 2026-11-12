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
