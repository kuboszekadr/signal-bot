from datetime import datetime, timedelta
from langchain.tools import tool

@tool
def get_current_date() -> str:
    """
    Get current date in YYYY-MM-DD format
    Returns:
        str: Current date as formatted string
    """
    return datetime.now().strftime("%Y-%m-%d")

@tool
def add_days(days: int, date_string: str = None) -> str:

    """
    Add specified number of days to a date.
    Args:
        days (int): Number of days to add (can be negative).
        str: New date in YYYY-MM-DD format, or an error message if the date format is invalid.
    Returns:
        str: New date in YYYY-MM-DD format
    """
    if date_string is None:
        date = datetime.now()
    else:
        date = datetime.strptime(date_string, "%Y-%m-%d")
    new_date = date + timedelta(days=days)
    return new_date.strftime("%Y-%m-%d")