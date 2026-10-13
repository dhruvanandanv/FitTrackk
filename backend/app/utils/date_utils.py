from datetime import datetime, date, timedelta, timezone


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_date(date_str: str) -> date:
    """Parses YYYY-MM-DD string to date object, falling back to today."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return datetime.now(timezone.utc).date()


def calculate_sleep_duration(start: datetime, end: datetime) -> int:
    """
    Calculates duration in minutes between start and end.
    Correctly handles overnight sleep when end is on the next day.
    If end <= start, assume it crossed midnight and add 1 day if not already included.
    """
    if end < start:
        # If timestamps don't have dates or end is recorded before start on clock
        end = end + timedelta(days=1)
    diff = end - start
    minutes = int(diff.total_seconds() / 60)
    return max(0, minutes)


def get_week_range(target_date: date):
    """Returns (start_of_week, end_of_week) where Monday is start and Sunday is end."""
    start = target_date - timedelta(days=target_date.weekday())
    end = start + timedelta(days=6)
    return start, end


def get_month_range(target_date: date):
    """Returns (start_of_month, end_of_month) for the given date."""
    start = target_date.replace(day=1)
    # Next month start minus 1 day
    if target_date.month == 12:
        next_month = target_date.replace(year=target_date.year + 1, month=1, day=1)
    else:
        next_month = target_date.replace(month=target_date.month + 1, day=1)
    end = next_month - timedelta(days=1)
    return start, end
