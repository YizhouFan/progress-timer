import json
import argparse

from datetime import datetime

from utils import human_readable_time_string

with open("example_project.json") as f:
    CONFIG = json.load(f)

with open("data/example_project.json") as f:
    DATA = json.load(f)


def update_start_ts(ts):
    DATA["sessions"].append({"start_ts": ts})
    DATA["status"] = "started"
    with open("data/example_project.json", "w") as f:
        json.dump(DATA, f, indent=4)


def update_stop_ts(ts):
    session = DATA["sessions"][-1]
    session["stop_ts"] = ts
    session["duration"] = ts - session["start_ts"]
    session["progress"] = []
    for tracker in CONFIG["progress_trackers"]:
        progress = int(input(f"Enter the progress of {tracker['name']}: "))
        session["progress"].append(
            {"tracker_name": tracker["name"], "progress": progress}
        )
    DATA["sessions"][-1] = session
    DATA["status"] = "stopped"
    with open("data/example_project.json", "w") as f:
        json.dump(DATA, f, indent=4)


def show_session_summary():
    latest_session = DATA["sessions"][-1]
    human_readable_time = human_readable_time_string(latest_session["duration"])
    total_duration = sum([s["duration"] for s in DATA["sessions"]])
    print(
        f"Good Job! You worked on {CONFIG['project_name']} for {human_readable_time} in this session. You've been working on it for {human_readable_time_string(total_duration)}."
    )
    for i, tracker in enumerate(CONFIG["progress_trackers"]):
        total_progress = sum([s["progress"][i]["progress"] for s in DATA["sessions"]])
        velocity = total_progress / total_duration
        forecasted_duration = tracker["total"] / velocity
        print(
            f"Progress for {tracker['name']} is now {total_progress}(+{latest_session['progress'][i]['progress']})/{tracker['total']} or {total_progress/tracker['total']*100:.2f}%(+{latest_session['progress'][i]['progress']/tracker['total']*100:.2f}%). The progress will be 100% in {human_readable_time_string(forecasted_duration)}."
        )


def start():
    if DATA["status"] == "stopped":
        ts = datetime.now().timestamp()
        update_start_ts(ts)
    elif DATA["status"] == "started":
        print(
            f"Project {CONFIG['project_name']} is already being timed. This will not do anything."
        )
    else:
        raise NotImplementedError(f"Unknown status {DATA['status']} detected!")


def stop():
    if DATA["status"] == "started":
        ts = datetime.now().timestamp()
        update_stop_ts(ts)
        show_session_summary()
    elif DATA["status"] == "stopped":
        print(
            f"Project {CONFIG['project_name']} is not being timed. This will not do anything. Here is the status of the latest session."
        )
        show_session_summary()
    else:
        raise NotImplementedError(f"Unknown status {DATA['status']} detected!")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode", type=str, help="Run mode. Now supports start, stop, and stats"
    )
    args = parser.parse_args()

    if args.mode == "start":
        start()
    elif args.mode == "stop":
        stop()
    elif args.mode == "stats":
        pass
    else:
        raise NotImplementedError(f"Run mode {args.mode} is not supported!")


if __name__ == "__main__":
    main()
