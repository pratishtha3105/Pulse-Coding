def validate_source(source):
    if source not in ["g2", "capterra"]:
        raise ValueError("Source must be g2 or capterra")

def validate_dates(start, end):
    if start > end:
        raise ValueError("Start date cannot be after end date")
