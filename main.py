# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-02-12 06:25:53
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-05 01:55:49
# FilePath: \Plugins\Wox.Base.Plugin.ChromeHistory\main.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

# -*- coding: utf-8 -*-
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from WoxBasePluginChromeQuery import *

from TimeStamp import *

class ChromeHistoryQuery(ChromeQuery):
    def __getDatas__(self):
        return ChromeCache.getHistories()

    def __getResult__(self, regex:RegexList, data:History):
        item = f'{data.platform.name};{data.title};{stamp2time(data.lastVisitTime, "toMicroSec")};{data.url}/'
        if not regex.match(item):
            return
        subTitle = '[{time}] {url}'.format(time=stamp2time(data.lastVisitTime, 'toSec'), url=data.url)
        return QueryResult(data.platform.name + ' ' + data.title,subTitle,data.icon,self.__datas__.index(data),self.openUrl.__name__,True,data.url).toDict()

    def __extraContextMenu__(self, data: History):
        lastVisitTime = stamp2time(data.lastVisitTime, 'toMicroSec')
        return [self.getCopyDataResult('Last Visit Time', lastVisitTime, data.icon)]

if __name__ == '__main__':
    # QueryChromeHistory().query('')
    ChromeHistoryQuery()
