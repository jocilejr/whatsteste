import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location("wfreal", pathlib.Path(__file__).resolve().parent.parent / "whatsflow-real.py")
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)


def test_compute_next_run_daily_timezone():
    dt = wf.compute_next_run("daily", 0, "00:00")
    assert dt.tzinfo == wf.BR_TZ


def test_compute_next_run_weekly_day():
    dt = wf.compute_next_run("weekly", 3, "12:00")
    assert dt.weekday() == 3
