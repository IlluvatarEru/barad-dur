import datetime


def get_current_timestamp():
    """
    get the current timestamp in micro seconds
    :return:
    """
    # this is a float with the micros after the decimal so multiply by 1000000
    return int(datetime.datetime.now().timestamp() * 1000000)
