from datetime import datetime
from zoneinfo import ZoneInfo 

def vn_now():
    return datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
