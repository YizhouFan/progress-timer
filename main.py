import argparse

from project import Project
from user import User


def main():
    USER_NAME = "user"
    user = User(USER_NAME)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        type=str,
        help="Run mode. Now supports start, stop, pause, unpause, stats, switch.",
    )
    args = parser.parse_args()
    mode = args.mode

    project = Project(user.default_project, user.projects_path, user.sessions_path)

    if mode == "start":
        project.start()
    elif mode == "stop":
        project.stop()
    elif mode == "pause":
        project.pause()
    elif mode == "unpause":
        project.unpause()
    elif mode == "stats":
        project.summary()
    elif mode == "switch":
        project_name = input(
            "Enter an existing project to set as the default, or name a new project name to set it up: "
        )
        user.update_default_project(project_name)
    else:
        raise NotImplementedError(f"Run mode {mode} is not supported!")


if __name__ == "__main__":
    main()
