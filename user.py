import glob
import json
from os import makedirs, path


class User:
    def __init__(self, name: str):
        self.config_file_path = path.join("settings", name + ".json")
        with open(self.config_file_path) as f:
            data = json.load(f)
        self.projects_path = data["projects_path"]
        self.sessions_path = data["sessions_path"]
        self.default_project = data["default_project"]
        makedirs(self.projects_path, exist_ok=True)
        makedirs(self.sessions_path, exist_ok=True)
        self.projects = glob.glob(path.join(self.projects_path, "*.json"))
        self.projects = [path.splitext(path.basename(p))[0] for p in self.projects]

    def make_new_project(self, name: str) -> None:
        assert name not in self.projects, f"Project {name} already exists!"
        trackers = []
        while True:
            tracker_name = input(f"Enter a new tracker for project {name}: ")
            if not tracker_name:
                break
            tracker_total = int(input(f"Enter the total amount for tracker {tracker_name}: "))
            if tracker_total <= 0:
                break
            trackers.append({"name": tracker_name, "total": tracker_total})
        assert len(trackers) > 0, f"Project {name} cannot be created with no valid trackers."

        project_config = {"project_name": name, "progress_trackers": trackers}
        project_config_path = path.join(self.projects_path, name + ".json")
        with open(project_config_path, "w") as f:
            json.dump(project_config, f, indent=4)

        project_sessions = {"status": "stopped", "sessions": []}
        project_sessions_path = path.join(self.sessions_path, name + ".json")
        with open(project_sessions_path, "w") as f:
            json.dump(project_sessions, f, indent=4)

        self.projects.append(name)
        print(f"Project {name} is successfully created.")

    def update_default_project(self, project: str) -> None:
        if project == self.default_project:
            print(f"{project} is already the default project. This will do nothing.")
            return
        if project not in self.projects:
            self.make_new_project(project)
        self.default_project = project
        with open(self.config_file_path, "w") as f:
            json.dump(self.package(), f, indent=4)
        print(f"{project} is now the default project.")

    def package(self) -> dict:
        return {
            "projects_path": self.projects_path,
            "sessions_path": self.sessions_path,
            "default_project": self.default_project,
        }
