import datetime

import pandas as pd
from dateutil.utils import today

MINUTES_PER_DAY = 24 * 60


def get_current_timestamp():
    """
    get the current timestamp in micro seconds
    :return:
    """
    # this is a float with the micros after the decimal so multiply by 1000000
    return datetime.datetime.now().timestamp()


def today_date():
    return today().date()


def timestamp_to_datetime(t):
    return datetime.datetime.fromtimestamp(t)


def timestamp_to_date(t):
    return timestamp_to_datetime(t).date()


def date_to_timestamp(d):
    return int(datetime.datetime.combine(d, datetime.datetime.min.time()).timestamp() * 1000)


def to_date(d):
    if type(d) == int:
        d = datetime.datetime.fromtimestamp(d / 1000)
    if type(d) == str:
        d = pd.to_datetime(d)
    if type(d) == pd._libs.tslibs.timestamps.Timestamp:
        d = d.date()
    if type(d) == datetime.datetime:
        d = d.date()
    check_date_is_datetime_date(d)
    return d


def check_date_is_datetime_date(d):
    if type(d) != datetime.date:
        raise Exception('Date should be datetime.date, it is:' + str(type(d)))


def add_days_to_date(date, days):
    return to_date(date + datetime.timedelta(days=days))
