import json
import argparse

from datetime import datetime

from utils import human_readable_time_string

with open("example_project.json") as f:
    CONFIG = json.load(f)

with open("data/example_project.json") as f:
    DATA = json.load(f)


def update_start_ts(ts):
    DATA["sessions"].append({"start_ts": ts, "latest_active_ts": ts})
    DATA["status"] = "started"
    with open("data/example_project.json", "w") as f:
        json.dump(DATA, f, indent=4)


def update_stop_ts(ts):
    session = DATA["sessions"][-1]
    session["stop_ts"] = ts
    session["duration"] = ts - session["start_ts"]
    if DATA["status"] == "unpaused":
        net_duration_list = session.get("net_duration", [])
        net_duration_list.append(ts - session["latest_active_ts"])
        session["net_duration"] = net_duration_list
    session["progress"] = input_progress()
    session["final_net_duration"] = sum(
        session.get("net_duration", [session["duration"]])
    )
    DATA["sessions"][-1] = session
    DATA["status"] = "stopped"
    with open("data/example_project.json", "w") as f:
        json.dump(DATA, f, indent=4)


def input_progress():
    result = []
    for tracker in CONFIG["progress_trackers"]:
        progress = int(input(f"Enter the progress of {tracker['name']}: "))
        result.append({"tracker_name": tracker["name"], "progress": progress})
    return result


def show_session_summary():
    latest_session = DATA["sessions"][-1]
    human_readable_time = human_readable_time_string(
        latest_session["final_net_duration"]
    )
    total_net_duration = sum([s["final_net_duration"] for s in DATA["sessions"]])
    print(
        f"Good Job! You worked on {CONFIG['project_name']} for {human_readable_time} in the latest session. "
        + f"You've been working on it for {human_readable_time_string(total_net_duration)}."
    )
    for i, tracker in enumerate(CONFIG["progress_trackers"]):
        total_progress = sum([s["progress"][i]["progress"] for s in DATA["sessions"]])
        velocity = total_progress / total_net_duration
        forecasted_remaining_duration = (tracker["total"] - total_progress) / velocity
        print(
            f"Progress for {tracker['name']} is now {total_progress}"
            + f"(+{latest_session['progress'][i]['progress']})/{tracker['total']} or "
            + f"{total_progress/tracker['total']*100:.2f}%"
            + f"(+{latest_session['progress'][i]['progress']/tracker['total']*100:.2f}%). "
            + f"The progress will be 100% in {human_readable_time_string(forecasted_remaining_duration)}."
        )


def update_pause_ts(ts):
    session = DATA["sessions"][-1]
    pause_ts_list = session.get("pause_ts", [])
    pause_ts_list.append(ts)
    session["pause_ts"] = pause_ts_list
    net_duration_list = session.get("net_duration", [])
    net_duration_list.append(ts - session["latest_active_ts"])
    session["net_duration"] = net_duration_list
    DATA["status"] = "paused"
    with open("data/example_project.json", "w") as f:
        json.dump(DATA, f, indent=4)


def update_unpause_ts(ts):
    session = DATA["sessions"][-1]
    unpause_ts_list = session.get("unpause_ts", [])
    unpause_ts_list.append(ts)
    session["unpause_ts"] = unpause_ts_list
    assert len(session["unpause_ts"]) == len(session["pause_ts"])
    session["latest_active_ts"] = ts
    DATA["status"] = "unpaused"
    with open("data/example_project.json", "w") as f:
        json.dump(DATA, f, indent=4)


def start():
    if DATA["status"] == "stopped":
        ts = datetime.now().timestamp()
        update_start_ts(ts)
        print("The session is now started.")
    elif DATA["status"] == "started":
        print(
            f"Project {CONFIG['project_name']} is already being timed. This will not do anything."
        )
    else:
        raise NotImplementedError(f"Unknown status {DATA['status']} detected!")


def stop():
    if DATA["status"] in ["started", "paused", "unpaused"]:
        ts = datetime.now().timestamp()
        update_stop_ts(ts)
        show_session_summary()
    elif DATA["status"] == "stopped":
        print(
            f"Project {CONFIG['project_name']} is not being timed. "
            + f"This will not do anything. Here is the status of the latest session."
        )
        show_session_summary()
    else:
        raise NotImplementedError(f"Unknown status {DATA['status']} detected!")


def pause():
    if DATA["status"] in ["started", "unpaused"]:
        ts = datetime.now().timestamp()
        update_pause_ts(ts)
        print("The session is now paused.")
    else:
        raise NotImplementedError(f"Unknown status {DATA['status']} detected!")


def unpause():
    if DATA["status"] == "paused":
        ts = datetime.now().timestamp()
        update_unpause_ts(ts)
        print("The session is now unpaused.")
    else:
        raise NotImplementedError(f"Unknown status {DATA['status']} detected!")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        type=str,
        help="Run mode. Now supports start, stop, pause, unpause, stats.",
    )
    args = parser.parse_args()

    if args.mode == "start":
        start()
    elif args.mode == "stop":
        stop()
    elif args.mode == "pause":
        pause()
    elif args.mode == "unpause":
        unpause()
    elif args.mode == "stats":
        show_session_summary()
    else:
        raise NotImplementedError(f"Run mode {args.mode} is not supported!")


if __name__ == "__main__":
    main()
