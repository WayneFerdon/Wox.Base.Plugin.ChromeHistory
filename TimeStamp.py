# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-10-05 16:49:45
# LastEditors: wayneferdon wayneferdon@hotmail.com
# LastEditTime: 2022-10-05 17:06:49
# FilePath: \undefinedc:\Users\WayneFerdon\AppData\Local\Wox\app-1.4.1196\Plugins\Wox.Plugin.ChromeHistory\TimeStamp.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

# -*- coding: utf-8 -*-
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