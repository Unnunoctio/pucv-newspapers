from datetime import datetime


class DateUtils:
    @staticmethod
    def diff_days(date1: datetime, date2: datetime) -> int:
        diff = date1 - date2
        return diff.days
