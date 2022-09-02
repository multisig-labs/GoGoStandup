import arrow


def next_time(seconds: int):
    # get the next day at midnight
    return arrow.now().shift(days=1).replace(hour=0, minute=0, second=0).shift(seconds=seconds).timestamp()
