import argparse
import glob
import json
from datetime import datetime
from os import path

from utils import human_readable_time_string

USER_CONFIG_PATH = "settings/user.json"
USER_CONFIG = {}
PROJECT_CONFIG = {}
PROJECT_DATA = {}

with open(USER_CONFIG_PATH) as f:
    USER_CONFIG = json.load(f)
    PROJECT_CONFIG_PATH = path.join(USER_CONFIG["projects_config_path"], USER_CONFIG["default_project"]) + ".json"
    PROJECT_DATA_PATH = path.join(USER_CONFIG["projects_data_path"], USER_CONFIG["default_project"]) + ".json"
with open(PROJECT_CONFIG_PATH) as f:
    PROJECT_CONFIG = json.load(f)
with open(PROJECT_DATA_PATH) as f:
    PROJECT_DATA = json.load(f)


def setup_new_project(project):
    pass


def update_default_project(project):
    projects = glob.glob(path.join(USER_CONFIG["projects_config_path"], "*.json"))
    if project not in projects:
        setup_new_project(project)
    USER_CONFIG["default_project"] = project


def update_start_ts(ts):
    PROJECT_DATA["sessions"].append({"start_ts": ts, "latest_active_ts": ts})
    PROJECT_DATA["status"] = "started"
    with open(PROJECT_DATA_PATH, "w") as f:
        json.dump(PROJECT_DATA, f, indent=4)


def update_stop_ts(ts):
    session = PROJECT_DATA["sessions"][-1]
    session["stop_ts"] = ts
    session["duration"] = ts - session["start_ts"]
    if PROJECT_DATA["status"] == "unpaused":
        net_duration_list = session.get("net_duration", [])
        net_duration_list.append(ts - session["latest_active_ts"])
        session["net_duration"] = net_duration_list
    session["progress"] = input_progress()
    session["final_net_duration"] = sum(session.get("net_duration", [session["duration"]]))
    PROJECT_DATA["sessions"][-1] = session
    PROJECT_DATA["status"] = "stopped"
    with open(PROJECT_DATA_PATH, "w") as f:
        json.dump(PROJECT_DATA, f, indent=4)


def input_progress():
    result = []
    for tracker in PROJECT_CONFIG["progress_trackers"]:
        progress = int(input(f"Enter the progress of {tracker['name']}: "))
        result.append({"tracker_name": tracker["name"], "progress": progress})
    return result


def show_session_summary():
    latest_session = PROJECT_DATA["sessions"][-1]
    human_readable_time = human_readable_time_string(latest_session["final_net_duration"])
    total_net_duration = sum([s["final_net_duration"] for s in PROJECT_DATA["sessions"]])
    print(
        f"Good Job! You worked on {PROJECT_CONFIG['project_name']} for {human_readable_time} in the latest session. "
        + f"You've been working on it for {human_readable_time_string(total_net_duration)}."
    )
    for i, tracker in enumerate(PROJECT_CONFIG["progress_trackers"]):
        total_progress = sum([s["progress"][i]["progress"] for s in PROJECT_DATA["sessions"]])
        velocity = total_progress / total_net_duration
        forecasted_remaining_duration = (tracker["total"] - total_progress) / velocity
        print(
            f"Progress for {tracker['name']} is now {total_progress}"
            + f"(+{latest_session['progress'][i]['progress']})/{tracker['total']} or "
            + f"{total_progress / tracker['total'] * 100:.2f}%"
            + f"(+{latest_session['progress'][i]['progress'] / tracker['total'] * 100:.2f}%). "
            + f"The progress will be 100% in {human_readable_time_string(forecasted_remaining_duration)}."
        )


def update_pause_ts(ts):
    session = PROJECT_DATA["sessions"][-1]
    pause_ts_list = session.get("pause_ts", [])
    pause_ts_list.append(ts)
    session["pause_ts"] = pause_ts_list
    net_duration_list = session.get("net_duration", [])
    net_duration_list.append(ts - session["latest_active_ts"])
    session["net_duration"] = net_duration_list
    PROJECT_DATA["status"] = "paused"
    with open(PROJECT_DATA_PATH, "w") as f:
        json.dump(PROJECT_DATA, f, indent=4)


def update_unpause_ts(ts):
    session = PROJECT_DATA["sessions"][-1]
    unpause_ts_list = session.get("unpause_ts", [])
    unpause_ts_list.append(ts)
    session["unpause_ts"] = unpause_ts_list
    assert len(session["unpause_ts"]) == len(session["pause_ts"])
    session["latest_active_ts"] = ts
    PROJECT_DATA["status"] = "unpaused"
    with open(PROJECT_DATA_PATH, "w") as f:
        json.dump(PROJECT_DATA, f, indent=4)


def start():
    print(PROJECT_DATA)
    print(PROJECT_CONFIG)
    if PROJECT_DATA["status"] == "stopped":
        ts = datetime.now().timestamp()
        update_start_ts(ts)
        print("The session is now started.")
    elif PROJECT_DATA["status"] == "started":
        print(f"Project {PROJECT_CONFIG['project_name']} is already being timed. This will not do anything.")
    else:
        raise NotImplementedError(f"Unknown status {PROJECT_DATA['status']} detected!")


def stop():
    if PROJECT_DATA["status"] in ["started", "paused", "unpaused"]:
        ts = datetime.now().timestamp()
        update_stop_ts(ts)
        show_session_summary()
    elif PROJECT_DATA["status"] == "stopped":
        print(
            f"Project {PROJECT_CONFIG['project_name']} is not being timed. "
            + "This will not do anything. Here is the status of the latest session."
        )
        show_session_summary()
    else:
        raise NotImplementedError(f"Unknown status {PROJECT_DATA['status']} detected!")


def pause():
    if PROJECT_DATA["status"] in ["started", "unpaused"]:
        ts = datetime.now().timestamp()
        update_pause_ts(ts)
        print("The session is now paused.")
    else:
        raise NotImplementedError(f"Unknown status {PROJECT_DATA['status']} detected!")


def unpause():
    if PROJECT_DATA["status"] == "paused":
        ts = datetime.now().timestamp()
        update_unpause_ts(ts)
        print("The session is now unpaused.")
    else:
        raise NotImplementedError(f"Unknown status {PROJECT_DATA['status']} detected!")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        type=str,
        help="Run mode. Now supports start, stop, pause, unpause, stats.",
    )
    parser.add_argument(
        "-p",
        "--project",
        type=str,
        help="Start a session with a specified project. The default project will be updated to this project. "
        + "Only works with the start run mode.",
    )
    args = parser.parse_args()

    project = args.project
    mode = args.mode
    if project and mode != "start":
        raise ValueError("The project parameter only works upon starting the session!")

    if args.mode == "start":
        if project:
            update_default_project(project)
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
