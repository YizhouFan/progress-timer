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
        help="Run mode. Now supports start, stop, pause, unpause, stats.",
    )
    args = parser.parse_args()

    project = Project(user.default_project, user.projects_path, user.sessions_path)

    if args.mode == "start":
        project.start()
    elif args.mode == "stop":
        project.stop()
    elif args.mode == "pause":
        project.pause()
    elif args.mode == "unpause":
        project.unpause()
    elif args.mode == "stats":
        project.summary()
    else:
        raise NotImplementedError(f"Run mode {args.mode} is not supported!")


if __name__ == "__main__":
    main()
