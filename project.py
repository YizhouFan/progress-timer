import json
from datetime import datetime
from os import path

from session import Session
from utils import human_readable_time_string


class Project:
    def __init__(self, name: str, projects_config_path: str, sessions_path: str):
        self.name = name
        self.config_file_path = path.join(projects_config_path, name + ".json")
        self.session_file_path = path.join(sessions_path, name + ".json")
        with open(self.config_file_path) as f:
            data = json.load(f)
        assert self.name == data["project_name"], f"Check project config file, {self.name}, {data['project_name']}"
        self.trackers = data["progress_trackers"]
        with open(self.session_file_path) as f:
            data = json.load(f)
        self.status = data["status"]
        self.sessions: list[Session] = []
        for s in data["sessions"]:
            self.sessions.append(Session(s))

    def latest_session(self) -> Session:
        return self.sessions[-1]

    def summary(self) -> None:
        human_readable_time = human_readable_time_string(self.latest_session().final_net_duration)
        total_net_duration = sum([s.final_net_duration for s in self.sessions])
        print(
            f"Good Job! You worked on {self.name} for {human_readable_time} in the latest session. "
            + f"You've been working on it for {human_readable_time_string(total_net_duration)}."
        )
        for i, tracker in enumerate(self.trackers):
            total_progress = sum([s.progress[i]["progress"] for s in self.sessions])
            velocity = total_progress / total_net_duration
            forecasted_remaining_duration = (tracker["total"] - total_progress) / velocity
            print(
                f"Progress for {tracker['name']} is now {total_progress}"
                + f"(+{self.latest_session().progress[i]['progress']})/{tracker['total']} or "
                + f"{total_progress / tracker['total'] * 100:.2f}%"
                + f"(+{self.latest_session().progress[i]['progress'] / tracker['total'] * 100:.2f}%). "
                + f"The progress will be 100% in {human_readable_time_string(forecasted_remaining_duration)}."
            )

    def stop(self) -> None:
        if self.status in ["started", "paused", "unpaused"]:
            ts = datetime.now().timestamp()
            self._update_stop_ts(ts)
            self.summary()
        elif self.status == "stopped":
            print(
                f"Project {self.name} is not being timed. "
                + "This will not do anything. Here is the status of the latest session."
            )
            self.summary()
        else:
            raise ValueError(f"Unknown status {self.status} detected!")

    def start(self) -> None:
        if self.status == "stopped":
            ts = datetime.now().timestamp()
            self._update_start_ts(ts)
            print("The session is now started.")
        elif self.status == "started":
            print(f"Project {self.name} is already being timed. This will not do anything.")
        else:
            raise ValueError(f"Unknown status {self.status} detected!")

    def pause(self) -> None:
        if self.status in ["started", "unpaused"]:
            ts = datetime.now().timestamp()
            self._update_pause_ts(ts)
            print("The session is now paused.")
        else:
            raise ValueError(f"Unknown status {self.status} detected!")

    def unpause(self) -> None:
        if self.status == "paused":
            ts = datetime.now().timestamp()
            self._update_unpause_ts(ts)
            print("The session is now unpaused.")
        else:
            raise ValueError(f"Unknown status {self.status} detected!")

    def dump_sessions_to_json(self) -> None:
        with open(self.session_file_path, "w") as f:
            json.dump({"status": self.status, "sessions": [s.package() for s in self.sessions]}, f, indent=4)

    def _input_progress(self) -> list[dict]:
        result = []
        for tracker in self.trackers:
            progress = int(input(f"Enter the progress of {tracker['name']}: "))
            result.append({"tracker_name": tracker["name"], "progress": progress})
        return result

    def _update_start_ts(self, ts: float) -> None:
        self.sessions.append(Session({"start_ts": ts, "latest_active_ts": ts}))
        self.status = "started"
        self.dump_sessions_to_json()

    def _update_stop_ts(self, ts: float) -> None:
        self.latest_session().stop_ts = ts
        self.latest_session().duration = ts - self.latest_session().start_ts
        if self.status == "unpaused":
            self.latest_session().net_duration.append(ts - self.latest_session().latest_active_ts)
        self.latest_session().progress = self._input_progress()
        if len(self.latest_session().net_duration) == 0:
            self.latest_session().net_duration = [self.latest_session().duration]
        self.latest_session().final_net_duration = sum(self.latest_session().net_duration)
        self.status = "stopped"
        self.dump_sessions_to_json()

    def _update_pause_ts(self, ts: float) -> None:
        self.latest_session().pause_ts.append(ts)
        self.latest_session().net_duration.append(ts - self.latest_session().latest_active_ts)
        self.status = "paused"
        self.dump_sessions_to_json()

    def _update_unpause_ts(self, ts: float) -> None:
        self.latest_session().unpause_ts.append(ts)
        assert len(self.latest_session().unpause_ts) == len(self.latest_session().pause_ts), (
            f"Times of pause {len(self.latest_session().pause_ts)} != unpause {len(self.latest_session().unpause_ts)}!"
        )
        self.latest_session().latest_active_ts = ts
        self.status = "unpaused"
        self.dump_sessions_to_json()
