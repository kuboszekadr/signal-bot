from .date import get_current_date, add_days
from .simple import simple_request
from .web_search import web_search_tool
from .summary_last_x_msgs import summarize_last_x_msgs


# FIXME
tools = {
    'simple_request': simple_request,
    'web_search_tool': web_search_tool,
    'get_current_date': get_current_date,
    'add_days': add_days,
    'summarize_last_x_msgs': summarize_last_x_msgs
}