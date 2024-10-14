from django import template
from datetime import timedelta
import calendar

register = template.Library()

@register.filter
def add_years(value, years):
    if not value:
        return value
    try:
        # Add the specified number of years
        new_year = value.year + int(years)
        # Adjust the date for leap years
        new_month = value.month
        new_day = value.day
        if new_month == 2 and new_day == 29:
            # If the date is February 29, check if the new year is a leap year
            if not calendar.isleap(new_year):
                new_day = 28
        return value.replace(year=new_year, month=new_month, day=new_day)
    except (ValueError, TypeError):
        return value
