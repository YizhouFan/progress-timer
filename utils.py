def human_readable_time_string(seconds):
    result = ""
    seconds
    hours = 0
    minutes = 0
    if seconds >= 3600:
        hours = seconds // 3600
        postfix = "hours" if hours > 1 else "hour"
        result += f"{hours:.0f} {postfix}"
    seconds -= hours * 3600
    if seconds >= 60:
        minutes = seconds // 60
        postfix = "minutes" if minutes > 1 else "minute"
        result += f" {minutes:.0f} {postfix}"
    seconds -= minutes * 60
    if seconds >= 1:
        postfix = "seconds" if seconds > 1 else "seconds"
        result += f" {seconds:.0f} {postfix}"
    result = result.strip()
    return result
