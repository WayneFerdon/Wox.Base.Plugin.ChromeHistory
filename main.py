# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-02-12 06:25:53
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-03-04 13:23:24
# FilePath: \Flow.Launcher.Plugin.ChromeHistory\main.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

# -*- coding: utf-8 -*-
from TimeStamp import *
from ChromeQuery import *

class GetHistory(ChromeQuery):
    def _getDatas_(self):
        return Cache.getHistories()

    def _getResult_(self, regex:RegexList, data:History):
        item = data.url + ';' + data.title + ';' + stamp2time(data.lastVisitTime, 'toMicroSec')
        if not regex.match(item):
            return
        subTitle = '[{time}] {url}'.format(time=stamp2time(data.lastVisitTime, 'toSec'), url=data.url)
        return QueryResult(data.title,subTitle,data.icon,self._datas_.index(data),self._openUrl_.__name__,True,data.url).toDict()

    def _extraContextMenu_(self, data: History):
        lastVisitTime = stamp2time(data.lastVisitTime, 'toMicroSec')
        return [self.getCopyDataResult('Last Visit Time', lastVisitTime, data.icon)]

if __name__ == '__main__':
    # GetHistory().query('')
    GetHistory()
