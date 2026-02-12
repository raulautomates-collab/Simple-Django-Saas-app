import datetime

#Retrieve current subscription start and end dates

def timetsamp_as_date(timestamp):
    return datetime.datetime.fromtimestamp(timestamp,tz=datetime.UTC)