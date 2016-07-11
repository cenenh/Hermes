import time
import datetime


def getToday():
    return time.strftime('%Y%m%d')


def getCurrentTime():
    return time.strftime("%H:%M:%S")


def getTimeDiff(start_time, end_time):
    start_dt = datetime.datetime.strptime(start_time, '%H:%M:%S')
    end_dt = datetime.datetime.strptime(end_time, '%H:%M:%S')
    diff = (end_dt - start_dt)
    return diff.seconds // 3600
