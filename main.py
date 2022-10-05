# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-02-12 06:25:53
# LastEditors: wayneferdon wayneferdon@hotmail.com
# LastEditTime: 2022-10-05 18:15:35
# FilePath: \Wox.Plugin.ChromeHistory\main.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

# -*- coding: utf-8 -*-
from TimeStamp import *
from ChromeWox import *

class GetHistory(ChromeWox):
    def getDatas(self):
        return self.cache.getHistories

    def getResult(self, regex, data:History):
        item = data.url + data.title + stamp2time(data.lastVisitTime, 'toMicroSec')
        if not regex.match(item):
            return
        if data.iconID != 0:
            iconPath = './Images/icon{}.png'.format(data.iconID)
        else:
            iconPath = self.PlatformIcon
        subTitle = '[{time}]{url}'.format(time=stamp2time(data.lastVisitTime, 'toSec'), url=data.url)
        return WoxResult(data.title,subTitle,iconPath,self.datas.index(data),self.openUrl.__name__,True,data.url).toDict()

    def extraContextMenu(self, data, iconPath):
        lastVisitTime = stamp2time(data.lastVisitTime, 'toMicroSec')
        return [self.getCopyDataResult('Last Visit Time', lastVisitTime, iconPath)]

if __name__ == '__main__':
    # GetHistory().query('')
    GetHistory()
