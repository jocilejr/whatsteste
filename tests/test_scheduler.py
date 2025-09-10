import os
import json
import threading
import tempfile
import sqlite3
from http.server import HTTPServer
from datetime import datetime, timedelta
import types
import sys

import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location("app", pathlib.Path(__file__).resolve().parents[1] / "whatsflow-real.py")
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class TestScheduleAPI:
    def setup_method(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)
        self.db_path = path
        app.DB_FILE = self.db_path
        app.init_db()
        self.server = HTTPServer(('127.0.0.1', 0), app.WhatsFlowRealHandler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def teardown_method(self):
        self.server.shutdown()
        self.thread.join()
        os.remove(self.db_path)

    def test_post_schedule_stores_data(self):
        import http.client

        payload = json.dumps({
            "instanceId": "t1",
            "groupId": "123@g.us",
            "content": "hello",
            "mediaType": "text",
            "recurrence": "daily",
            "sendTime": "10:00"
        })
        headers = {"Content-Type": "application/json"}
        conn = http.client.HTTPConnection('127.0.0.1', self.port)
        conn.request('POST', '/api/messages/schedule', payload, headers)
        resp = conn.getresponse()
        data = json.loads(resp.read().decode())
        assert data.get('success')

        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute("SELECT instance_id, group_id, recurrence FROM scheduled_messages")
        row = cur.fetchone()
        con.close()
        assert row == ('t1', '123@g.us', 'daily')


class TestSchedulerProcessing:
    def setup_method(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)
        self.db_path = path
        app.DB_FILE = self.db_path
        app.init_db()

    def teardown_method(self):
        os.remove(self.db_path)

    def test_daily_weekly_items_processed(self):
        now = datetime.now()
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO scheduled_messages (id, instance_id, group_id, content, media_type, media_path, recurrence, weekday, send_time, next_run) VALUES (?,?,?,?,?,?,?,?,?,?)",
            ("d1", "i", "g1", "m", "text", None, "daily", None, "00:00", (now - timedelta(minutes=1)).isoformat()),
        )
        cur.execute(
            "INSERT INTO scheduled_messages (id, instance_id, group_id, content, media_type, media_path, recurrence, weekday, send_time, next_run) VALUES (?,?,?,?,?,?,?,?,?,?)",
            ("w1", "i", "g2", "m", "text", None, "weekly", now.weekday(), "00:00", (now - timedelta(minutes=1)).isoformat()),
        )
        conn.commit()
        conn.close()

        calls = []

        def fake_send(inst, grp, content, mtype, mpath):
            calls.append(grp)
            return True

        orig = app.send_scheduled_message
        app.send_scheduled_message = fake_send
        app.process_scheduled_messages(now=now)
        app.send_scheduled_message = orig
        assert calls == ['g1', 'g2']

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT next_run FROM scheduled_messages WHERE id='d1'")
        next_daily = datetime.fromisoformat(cur.fetchone()[0])
        cur.execute("SELECT next_run FROM scheduled_messages WHERE id='w1'")
        next_weekly = datetime.fromisoformat(cur.fetchone()[0])
        conn.close()

        assert next_daily.date() == (now + timedelta(days=1)).date()
        assert next_weekly.date() == (now + timedelta(days=7)).date()

    def test_once_removed_after_send(self):
        now = datetime.now()
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO scheduled_messages (id, instance_id, group_id, content, media_type, media_path, recurrence, weekday, send_time, next_run) VALUES (?,?,?,?,?,?,?,?,?,?)",
            ("o1", "i", "g3", "m", "text", None, "once", None, "00:00", (now - timedelta(minutes=1)).isoformat()),
        )
        conn.commit()
        conn.close()

        orig = app.send_scheduled_message
        app.send_scheduled_message = lambda *a, **k: True
        app.process_scheduled_messages(now=now)
        app.send_scheduled_message = orig
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM scheduled_messages WHERE id='o1'")
        remaining = cur.fetchone()[0]
        conn.close()
        assert remaining == 0


class TestMediaDelivery:
    def test_media_sent_via_baileys(self):
        fd, path = tempfile.mkstemp()
        os.write(fd, b'data')
        os.close(fd)

        sent = {}

        def fake_post(url, data):
            sent['payload'] = data

        app.baileys_post = fake_post

        ok = app.send_scheduled_message('i', 'g', 'msg', 'image', path)
        os.remove(path)
        assert ok
        assert 'image' in sent['payload']

