import arrow

WEEK = ["m", "t", "w", "th", "f", "s", "su"]


def next_time(seconds: int, tz: str = 'utc', days: list[str] = []) -> float:
    now = arrow.now(tz)
    t = now.replace(hour=0, minute=0, second=0).shift(
        seconds=seconds)
    if t.timestamp() > now.timestamp():
        return t.to('utc').timestamp()
    weekday = now.weekday()
    if days:
        valid_days = [WEEK.index(day) for day in days if day in WEEK]
        shift = 1
        while not weekday in valid_days:
            weekday = (weekday + shift) % 7
            shift += 1
        t = t.shift(days=shift)
    else:
        if weekday == 4:
            t = t.shift(days=3)
        else:
            t = t.shift(days=1)
    return t.to('utc').timestamp()
