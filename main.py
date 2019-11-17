# -*- coding: utf-8 -*-
# require pypiwin32, can be install by pip
from wox import Wox, WoxAPI
import os
import sqlite3
import shutil
import re
import webbrowser
import win32con
import win32clipboard
import time
import datetime
from urllib.parse import urlparse


def stamp2time(timeStamp, timeFormat):
    baseDate = datetime.datetime(1601, 1, 1)
    yearSec = timeStamp / 1000000
    trueYearSec = baseDate + datetime.timedelta(seconds=yearSec, hours=8)
    toSec = time.strftime('%Y-%m-%d %H:%M:%S', datetime.datetime.timetuple(trueYearSec))
    if timeFormat == 'toSec':
        return toSec
    microSec = timeStamp % 1000
    milliSec = (timeStamp % 1000000 - microSec) // 1000
    toMilliSec = toSec + '.' + str(milliSec).zfill(3)
    if timeFormat == 'toMilliSec':
        return toMilliSec
    toMicroSec = toMilliSec + ' ' + str(microSec).zfill(3)
    if timeFormat == 'toMicroSec':
        return toMicroSec


def getTimeFromHisList(hisList):
    return hisList['lastVisitTime']


class getHistory(Wox):
# class getHistory():
    # <editor-fold desc="set paths of history database and icon database">
    localAppData = os.environ['localAppData'.upper()]
    dataPath = localAppData + '/Google/Chrome/User Data/Default'
    his = dataPath + '/History'
    favIcons = dataPath + '/Favicons'
    hisToRead = dataPath + '/HistoryToRead'
    favIconsToRead = dataPath + '/FaviconsToRead'
    # </editor-fold>

    # <editor-fold desc="create a read-only copy">
    shutil.copyfile(his, hisToRead)
    shutil.copyfile(favIcons, favIconsToRead)
    # </editor-fold>

    # <editor-fold desc="connect to database copy">
    favIconsCursor = sqlite3.connect(favIconsToRead).cursor()
    hisCursor = sqlite3.connect(hisToRead).cursor()
    # </editor-fold>

    # <editor-fold desc="create icon image temps">
    bitmapSelectStatement = 'SELECT icon_id, image_data, width, height ' \
                            'FROM favicon_bitmaps'
    favIconsCursor.execute(bitmapSelectStatement)
    bitmapCursorResults = favIconsCursor.fetchall()
    bitmapInfoList = dict()
    for iconId, imageData, width, height in bitmapCursorResults:
        if iconId in bitmapInfoList.keys():
            if width < bitmapInfoList[iconId][0] or height < bitmapInfoList[iconId][1]:
                continue
        with open('./Images/iconId{}.png'.format(iconId), 'wb') as f:
            f.write(imageData)
        bitmapInfoList.update(
            {
                iconId: [width, height]
            }
        )
    # </editor-fold>

    # <editor-fold desc="get url icon id"
    urlSelectStatement = 'SELECT page_url, icon_id ' \
                         'FROM icon_mapping'
    favIconsCursor.execute(urlSelectStatement)
    urlCursorResults = favIconsCursor.fetchall()
    iconList = dict()
    for url, iconId in urlCursorResults:
        netLocation = urlparse(url).netloc
        if netLocation in iconList.keys():
            continue
        else:
            iconList.update(
                {
                    netLocation: iconId
                }
            )
    # </editor-fold>

    favIconsCursor.close()

    # <editor-fold desc="get history info">
    hisSelectStatement = 'SELECT urls.url, urls.title, urls.last_visit_time ' \
                         'FROM urls, visits ' \
                         'WHERE urls.id = visits.url'
    hisCursor.execute(hisSelectStatement)
    hisCursorResults = hisCursor.fetchall()
    hisList = []
    items = []
    for url, title, lastVisitTime in hisCursorResults:
        item = url + title
        if item in items:
            itemIndex = items.index(item)
            if hisList[itemIndex]['lastVisitTime'] < lastVisitTime:
                hisList[itemIndex]['lastVisitTime'] = lastVisitTime
            continue
        items.append(item)
        netLocation = urlparse(url).netloc
        if netLocation in iconList.keys():
            iconId = iconList[netLocation]
        else:
            iconId = 0
        hisList.append(
            {
                'url': url,
                'title': title,
                'item': item,
                'lastVisitTime': lastVisitTime,
                'iconId': iconId
            }
        )
    hisList.sort(key=getTimeFromHisList, reverse=True)
    # </editor-fold>

    hisCursor.close()

    def query(self, queryString):
        # import history list
        result = []
        hisList = self.hisList

        # process query
        queryStringLower = queryString.lower()
        queryList = queryStringLower.split()
        regexList = []
        for query in queryList:
            # pattern = '.*?'.join(query)
            # regexList.append(re.compile(pattern))
            regexList.append(re.compile(query))

        # set result
        for his in hisList:
            itemWithTime = his['item'] + stamp2time(his['lastVisitTime'], 'toMicroSec')
            match = True
            for regex in regexList:
                match = regex.search(itemWithTime.lower()) and match
            if match:
                hisIndex = hisList.index(his)
                lastVisitTime = stamp2time(his['lastVisitTime'], 'toSec')
                url = his['url']
                if his['iconId'] != 0:
                    iconPath = './Images/iconId{}.png'.format(his['iconId'])
                else:
                    iconPath = './Images/chromeIcon.png'
                result.append(
                    {
                        'Title': his['title'],
                        'SubTitle': '[{time}]{url}'.format(time=lastVisitTime, url=url),
                        'IcoPath': iconPath,
                        'ContextData': hisIndex,
                        'JsonRPCAction': {
                            'method': 'openUrl',
                            'parameters': [url],
                            "dontHideAfterAction": False
                        }
                    }
                )
        return result

    def context_menu(self, hisIndex):
        his = self.hisList[hisIndex]
        url = his['url']
        title = his['title']
        if his['iconId'] != 0:
            iconPath = './Images/iconId{}.png'.format(his['iconId'])
        else:
            iconPath = './Images/chromeIcon.png'
        lastVisitTime = stamp2time(his['lastVisitTime'], 'toMicroSec')
        results = [{
            'Title': 'URL: ' + url,
            'SubTitle': 'Press Enter to Copy URL',
            'IcoPath': iconPath,
            'JsonRPCAction': {
                'method': 'copyData',
                'parameters': [url],
                "dontHideAfterAction": False
            }
        }, {
            'Title': 'Title: ' + title,
            'SubTitle': 'Press Enter to Copy Title',
            'IcoPath': iconPath,
            'JsonRPCAction': {
                'method': 'copyData',
                'parameters': [title],
                "dontHideAfterAction": False
            }
        }, {
            'Title': 'Last Visit Time: ' + lastVisitTime,
            'SubTitle': 'Press Enter to Copy Last Visit Time',
            'IcoPath': iconPath,
            'JsonRPCAction': {
                'method': 'copyData',
                'parameters': [lastVisitTime],
                "dontHideAfterAction": False
            }
        }]
        return results

    @classmethod
    def openUrl(cls, url):
        webbrowser.open(url)

    @classmethod
    def copyData(cls, data):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, data)
        win32clipboard.CloseClipboard()


if __name__ == '__main__':
    getHistory()
