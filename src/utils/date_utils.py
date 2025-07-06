from datetime import datetime

class DateUtils:
    @staticmethod
    def diff_days(date1: datetime, date2: datetime) -> int:
        diff = date1 - date2
        return diff.days
    
    @staticmethod
    def validate_date(date: str, error_message: str) -> datetime:
        try:
            return datetime.strptime(date, "%d-%m-%Y")
        except Exception:
            raise ValueError(error_message)
    
    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> None:
        current_date = datetime.now()
        if start_date > current_date:
            raise ValueError("La fecha de inicio debe ser menor a la fecha actual")
        if end_date > current_date:
            raise ValueError("La fecha de fin no debe ser mayor a la fecha actual")
        if start_date > end_date:
            raise ValueError("La fecha de inicio no debe ser mayor a la fecha de fin")