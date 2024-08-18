
import datetime
from calendar import monthrange

def week_of_month(dt):
    """ Returns the week of the month for the specified date.
    """
    first_day = dt.replace(day=1)
    first_day_weekday = first_day.weekday()
    adjusted_dom = dt.day + first_day_weekday
    return int(ceil(adjusted_dom/7.0))

def weeks_in_month(year, month):
    """ Returns the number of weeks in the specified month.
    """
    last_day = monthrange(year, month)[1]
    first_day = datetime.date(year, month, 1)
    last_date = datetime.date(year, month, last_day)
    return last_date.isocalendar()[1] - first_day.isocalendar()[1] + 1

def assign_week_to_month(year):
    """ Assigns each week of the year to the corresponding month.
    """
    week_month_map = {}
    for month in range(1, 13):
        first_day_of_month = datetime.date(year, month, 1)
        last_day_of_month = datetime.date(year, month, monthrange(year, month)[1])

        first_week = first_day_of_month.isocalendar()[1]
        last_week = last_day_of_month.isocalendar()[1]

        # Handle the edge case where December has weeks spilling into the next year's week 1
        if month == 12 and last_week == 1:
            last_week = 52

        for week in range(first_week, last_week + 1):
            if week not in week_month_map:
                week_month_map[week] = month

    return week_month_map

# # Example usage:
# # year = 2024
# # week_month_map = assign_week_to_month(year)
# # for week, month in sorted(week_month_map.items()):
# #     print(f"Week {week} is in month {month}")
