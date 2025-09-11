import json
import os
import threading
import tempfile
import sqlite3
from http.server import HTTPServer
from datetime import datetime, timedelta

import importlib.util
import pathlib

# Load application module
spec = importlib.util.spec_from_file_location(
    "app", pathlib.Path(__file__).resolve().parents[1] / "whatsflow-real.py"
)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class BaseServerTest:
    def setup_method(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)
        self.db_path = path
        app.DB_FILE = self.db_path
        app.init_db()
        self.server = HTTPServer(("127.0.0.1", 0), app.WhatsFlowRealHandler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def teardown_method(self):
        self.server.shutdown()
        self.thread.join()
        os.remove(self.db_path)


class TestCampaignCRUD(BaseServerTest):
    def test_campaign_crud(self):
        import http.client

        payload = json.dumps(
            {
                "name": "Camp1",
                "description": "d",
                "recurrence": "daily",
                "send_time": "10:00",
            }
        )
        headers = {"Content-Type": "application/json"}
        conn = http.client.HTTPConnection("127.0.0.1", self.port)
        conn.request("POST", "/api/campaigns", payload, headers)
        resp = conn.getresponse()
        data = json.loads(resp.read().decode())
        cid = data["campaign_id"]

        conn.request("GET", "/api/campaigns")
        resp = conn.getresponse()
        items = json.loads(resp.read().decode())
        assert any(c["id"] == cid for c in items)

        update = json.dumps({"name": "Camp2"})
        conn.request("PUT", f"/api/campaigns/{cid}", update, headers)
        conn.getresponse().read()

        conn.request("GET", f"/api/campaigns/{cid}")
        resp = conn.getresponse()
        item = json.loads(resp.read().decode())
        assert item["name"] == "Camp2"

        conn.request("DELETE", f"/api/campaigns/{cid}")
        conn.getresponse().read()

        conn.request("GET", "/api/campaigns")
        resp = conn.getresponse()
        items = json.loads(resp.read().decode())
        assert not items


class TestScheduleAPI(BaseServerTest):
    def create_campaign(self):
        import http.client
        payload = json.dumps(
            {
                "name": "Camp",
                "recurrence": "daily",
                "send_time": "10:00",
            }
        )
        headers = {"Content-Type": "application/json"}
        conn = http.client.HTTPConnection("127.0.0.1", self.port)
        conn.request("POST", "/api/campaigns", payload, headers)
        resp = conn.getresponse()
        return json.loads(resp.read().decode())["campaign_id"]

    def test_post_schedule_stores_data(self):
        import http.client

        cid = self.create_campaign()
        payload = json.dumps(
            {
                "campaign_id": cid,
                "content": "hello",
                "media_type": "text",
                "groups": ["123@g.us"],
            }
        )
        headers = {"Content-Type": "application/json"}
        conn = http.client.HTTPConnection("127.0.0.1", self.port)
        conn.request("POST", "/api/messages/schedule", payload, headers)
        resp = conn.getresponse()
        data = json.loads(resp.read().decode())
        assert data.get("success")

        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute("SELECT campaign_id, content FROM scheduled_messages")
        row = cur.fetchone()
        cur.execute("SELECT group_id FROM campaign_groups")
        grp = cur.fetchone()[0]
        con.close()
        assert row[0] == cid and grp == "123@g.us"


class TestDispatcherProcessing:
    def setup_method(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)
        self.db_path = path
        app.DB_FILE = self.db_path
        app.init_db()

    def teardown_method(self):
        os.remove(self.db_path)

    def test_recurring_and_once(self):
        now = datetime.now()
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO campaigns (id, name, recurrence, send_time, weekday) VALUES (?,?,?,?,?)",
            ("c1", "C", "daily", "00:00", None),
        )
        cur.execute(
            "INSERT INTO campaigns (id, name, recurrence, send_time, weekday) VALUES (?,?,?,?,?)",
            ("c2", "C2", "once", "00:00", None),
        )
        cur.execute(
            "INSERT INTO campaign_groups (campaign_id, group_id) VALUES (?,?)",
            ("c1", "g1"),
        )
        cur.execute(
            "INSERT INTO campaign_groups (campaign_id, group_id) VALUES (?,?)",
            ("c1", "g2"),
        )
        cur.execute(
            "INSERT INTO campaign_groups (campaign_id, group_id) VALUES (?,?)",
            ("c2", "g3"),
        )
        past = (now - timedelta(minutes=1)).isoformat()
        cur.execute(
            "INSERT INTO scheduled_messages (id, campaign_id, content, media_type, media_path, next_run, status) VALUES (?,?,?,?,?,?,?)",
            ("s1", "c1", "m", "text", None, past, "pending"),
        )
        cur.execute(
            "INSERT INTO scheduled_messages (id, campaign_id, content, media_type, media_path, next_run, status) VALUES (?,?,?,?,?,?,?)",
            ("s2", "c2", "m", "text", None, past, "pending"),
        )
        conn.commit()
        conn.close()

        calls = []

        def fake_send(group, content, mtype, mpath, instance_id="default"):
            calls.append(group)
            return True

        orig = app.send_scheduled_message
        app.send_scheduled_message = fake_send
        app.process_scheduled_messages(now=now)
        app.send_scheduled_message = orig

        assert calls == ["g1", "g2", "g3"]

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT status FROM scheduled_messages WHERE id='s2'")
        assert cur.fetchone()[0] == 'sent'
        cur.execute("SELECT next_run FROM scheduled_messages WHERE id='s1'")
        next_run = datetime.fromisoformat(cur.fetchone()[0])
        conn.close()
        assert next_run.date() == (now + timedelta(days=1)).date()


class TestMediaDelivery:
    def test_media_sent_via_baileys(self):
        fd, path = tempfile.mkstemp()
        os.write(fd, b'data')
        os.close(fd)

        sent = {}

        def fake_post(url, data):
            sent['payload'] = data

        app.baileys_post = fake_post
        ok = app.send_scheduled_message('g', 'msg', 'audio', path)
        os.remove(path)
        assert ok and 'audio' in sent['payload']

