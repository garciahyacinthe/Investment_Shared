import datetime as dt

def to_datetime(from_date, app_source):

    if app_source == 'WealthSimple':
        to_date = dt.date(day=int(from_date[8:10]), month=int(from_date[5:7]), year=int(from_date[:4]))
        return to_date

def yesterday(today, dayoffs=[]):

    #TODO add calendars
    yesterday = today - dt.timedelta(3 if today.weekday() == 0 else 1)

    while yesterday in dayoffs:
        yesterday = yesterday - dt.timedelta(3 if today.weekday() == 0 else 1)

    return yesterday