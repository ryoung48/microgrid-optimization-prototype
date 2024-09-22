from joblib import Memory

# setup job lib cache
mem_cache = Memory('cache')


from datetime import datetime, timedelta

def comparable_date(date: str) -> str:
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    comparable_date_obj = date_obj - timedelta(days=364)
    return comparable_date_obj.strftime("%Y-%m-%d")
