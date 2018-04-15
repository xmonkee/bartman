from datetime import datetime


def pad_zero(n):
    if len(n) == 2:
        return n
    if len(n) == 1:
        return '0' + n
    raise Exception('Received a value with too many digits')


class Clock(object):
    def get(self):
        now = datetime.now()
        hour = pad_zero(str(now.hour))
        minute = pad_zero(str(now.minute))
        return hour + minute

    def stop(self):
        return

