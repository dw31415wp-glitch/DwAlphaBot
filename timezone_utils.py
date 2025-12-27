from datetime import datetime, timezone
from dateutil.parser import parse

def ensure_utc(dt):
    if isinstance(dt, str):
        dt = parse(dt)
    
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    elif dt.tzinfo != timezone.utc:
        dt = dt.astimezone(timezone.utc)
    
    return dt

def now_utc():
    return datetime.now(timezone.utc)

def from_timestamp_utc(timestamp):
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)

def to_utc_string(dt):
    return ensure_utc(dt).isoformat()