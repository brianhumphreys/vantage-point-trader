from datetime import timedelta, datetime

def trade_days(date: str):
    date_parts = [int(x) for x in date.split('-')]
    day = datetime(date_parts[0], date_parts[1], date_parts[2], 0, 0)
    nextday = day + timedelta(days=1)
    return (day, nextday)