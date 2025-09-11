import os
import sqlite3
import tempfile
from datetime import datetime, timedelta, timezone
import importlib.util
import pathlib
import pytest

# Load application module
spec = importlib.util.spec_from_file_location(
    "app", pathlib.Path(__file__).resolve().parents[1] / "whatsflow-real.py"
)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    app.DB_FILE = path
    app.init_db()
    try:
        yield path
    finally:
        os.remove(path)


@pytest.fixture
def fake_baileys(monkeypatch):
    calls = []

    def _fake(url, data):
        calls.append({"url": url, "data": data})

    monkeypatch.setattr(app, "baileys_post", _fake)
    return calls


@pytest.mark.parametrize("media_type", ["image", "audio", "video"])
def test_scheduler_sends_media_to_multiple_groups(temp_db, fake_baileys, media_type):
    now = datetime.now(app.BR_TZ)
    conn = sqlite3.connect(temp_db)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO campaigns (id, name, recurrence, send_time, weekday) VALUES (?,?,?,?,?)",
        ("c1", "C", "once", "00:00", None),
    )
    for g in ("g1", "g2"):
        cur.execute(
            "INSERT INTO campaign_groups (campaign_id, group_id) VALUES (?,?)",
            ("c1", g),
        )
    fd, mpath = tempfile.mkstemp()
    os.write(fd, b"data")
    os.close(fd)
    past = (now - timedelta(minutes=1)).astimezone(timezone.utc).isoformat()
    cur.execute(
        "INSERT INTO scheduled_messages (id, campaign_id, content, media_type, media_path, next_run, status) VALUES (?,?,?,?,?,?,?)",
        ("s1", "c1", "hello", media_type, mpath, past, "pending"),
    )
    conn.commit()
    conn.close()

    app.process_scheduled_messages(now=now)
    os.remove(mpath)

    assert len(fake_baileys) == 2
    groups = ["g1", "g2"]
    for call, group in zip(fake_baileys, groups):
        assert call["data"]["to"] == group
        assert media_type in call["data"]

    conn = sqlite3.connect(temp_db)
    cur = conn.cursor()
    cur.execute("SELECT status FROM scheduled_messages WHERE id='s1'")
    assert cur.fetchone()[0] == "sent"
    conn.close()
