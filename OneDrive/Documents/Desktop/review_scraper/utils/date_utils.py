from dateutil import parser

def parse_date(date_str):
    return parser.parse(date_str).date()

def is_within_range(date, start, end):
    return start <= date <= end
