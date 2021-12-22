""" module for various python utility functions """
from datetime import datetime
import bleach
import markdown

def format_time(utc):
    """ Formats a date as Month (English name) DD, YYYY"""

    return datetime.strftime(utc, "%B %d, %Y")

def format_time_ago(value, unit):
    if value == 1:
        return f'1 {unit} ago'
    return f'{value} {unit}s ago'

def time_ago(utc):
    """ 
    Gets delta of time, in appropriate units 
     - Less than hour expressed in minutes
     - Less than day = hours
     - Less than week = days
     - Less than month = weeks
     - Less than year = months
     - year >= 1, = years.
    """

    seconds = (datetime.utcnow() - utc).seconds
    if seconds < 60:
        return format_time_ago(seconds, 'second')
    minutes = seconds // 60
    if minutes < 60:
        return format_time_ago(minutes, 'minute')
    hours = minutes // 60
    if hours < 24:
        return format_time_ago(hours, 'hour')
    days = hours // 24
    if days < 7:
        return format_time_ago(days, 'day')
    weeks = days // 7
    if weeks <= 4:
        return format_time_ago(weeks, 'week')
    months = weeks // 4
    if months < 12:
        return format_time_ago(months, 'month')
    years = months // 12
    return format_time(years, 'year')

def markdown_into_sanitized_html(md):
    """ Code heavily inspired by Flask-MDE template code """
    html = markdown.markdown(
            md,
            extensions=['nl2br', 'smarty', 'pymdownx.tilde', 'extra'])
    allowed_tags = [
        'a', 'abbr', 'acronym', 'b', 'blockquote', 'br',
        'code', 'dd', 'del', 'div', 'dl', 'dt', 'em',
        'em', 'h1', 'h2', 'h3', 'hr', 'i', 'img', 'li',
        'ol', 'p', 'pre', 's', 'strong', 'sub', 'sup',
        'table', 'tbody', 'td', 'th', 'thead', 'tr', 'ul'
    ]
    allowed_attrs = {
        '*': ['class'],
        'a': ['href', 'rel'],
        'img': ['src', 'alt']
    }
    sanitized_html = bleach.clean(
        bleach.linkify(html),
        tags=allowed_tags,
        attributes=allowed_attrs
    )
    return sanitized_html
