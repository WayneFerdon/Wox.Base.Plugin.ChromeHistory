import time
import datetime

def stamp2time(timeStamp, timeFormat) -> str:
    baseDate = datetime.datetime(1601, 1, 1)
    yearSec = timeStamp / 1000000
    trueYearSec = baseDate + datetime.timedelta(seconds=yearSec, hours=8)
    toSec = time.strftime('%Y-%m-%d %H:%M:%S', datetime.datetime.timetuple(trueYearSec))
    if timeFormat == 'toSec':
        return toSec
    microSec = timeStamp % 1000
    milliSec = (timeStamp % 1000000 - microSec) // 1000
    toMilliSec = toSec + '.' + str(milliSec).zfill(3)
    # if timeFormat == 'toMilliSec':
    #     return toMilliSec
    toMicroSec = toMilliSec + ' ' + str(microSec).zfill(3)
    if timeFormat == 'toMicroSec':
        return toMicroSec