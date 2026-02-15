import datetime

#Retrieve current subscription start and end dates

def timestamp_as_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp,tz=datetime.UTC)#returns an integer as a timestamp