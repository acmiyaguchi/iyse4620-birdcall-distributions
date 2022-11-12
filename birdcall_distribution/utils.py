def convert_time(ts: str) -> float:
    """Convert hh:mm strings into hours since midnight."""
    try:
        hour, minute = ts.split(":")
        return int(hour) + int(minute) / 60
    except:
        # xx:xx
        return float("nan")
