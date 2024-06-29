from datetime import datetime
import calendar

blacklist = set()

def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in blacklist

def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return datetime(year, month, day)

def add_days(source_date, days):
    return source_date + timedelta(days=days)

def add_years(source_date, years):
    year = source_date.year + years
    month = source_date.month
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return datetime(year, month, day)
    
def calculate_new_expiry_date(current_expiry, interval_unit, interval_count):
    if interval_unit == 'MONTH':
        new_expiry_date = add_months(current_expiry, interval_count)
        return new_expiry_date
    elif interval_unit == 'DAY':
        new_expiry_date = add_days(current_expiry, interval_count)
    elif interval_unit == 'YEAR':
        new_expiry_date = add_years(current_expiry, interval_count)
    else:
        raise ValueError("Unsupported interval unit")