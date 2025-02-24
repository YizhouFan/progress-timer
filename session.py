class Session:
    def __init__(self, config: dict):
        self.start_ts = config["start_ts"]
        self.latest_active_ts = config["latest_active_ts"]
        self.pause_ts = config.get("pause_ts", [])
        self.net_duration = config.get("net_duration", [])
        self.unpause_ts = config.get("unpause_ts", [])
        self.stop_ts = config.get("stop_ts", None)
        self.duration = config.get("duration", None)
        self.progress = config.get("progress", [])
        self.final_net_duration = config.get("final_net_duration", None)

    def package(self) -> dict:
        return {
            "start_ts": self.start_ts,
            "latest_active_ts": self.latest_active_ts,
            "pause_ts": self.pause_ts,
            "net_duration": self.net_duration,
            "unpause_ts": self.unpause_ts,
            "stop_ts": self.stop_ts,
            "duration": self.duration,
            "progress": self.progress,
            "final_net_duration": self.final_net_duration,
        }
