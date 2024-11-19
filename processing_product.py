import datetime


date = datetime.datetime.now(datetime.UTC).date()
print(date+datetime.timedelta(days=10))
