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

TargetPlatform = "Chrome" # Chrome, Edge

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
    # if timeFormat == 'toMilliSec':
    #     return toMilliSec
    toMicroSec = toMilliSec + ' ' + str(microSec).zfill(3)
    if timeFormat == 'toMicroSec':
        return toMicroSec


def timeFromHisList(hisList):
    return hisList['lastVisitTime']


def createIcon(bitmapInfoList):
    for iconId in bitmapInfoList.keys():
        imageData = bitmapInfoList[iconId]['imageData']
        with open('./Images/iconId{}.png'.format(iconId), 'wb') as f:
            f.write(imageData)


class chromeCache:
    def __init__(self):
        localAppData = os.environ['localAppData'.upper()]
        if(TargetPlatform == "Chrome"):
            self.__dataPath__ = localAppData + '/Google/Chrome/User Data/Default'
        elif(TargetPlatform == "Edge"):
            self.__dataPath__ = localAppData + '/Microsoft/Edge/User Data/Default'
        self.bitmapInfoList, self.iconList = self._iconInfo_()

    def _iconData_(self):
        favIcons = self.__dataPath__ + '/Favicons'
        iconData = self.__dataPath__ + '/FaviconsToRead'
        shutil.copyfile(favIcons, iconData)
        return iconData

    def _hisData_(self):
        his = self.__dataPath__ + '/History'
        hisData = self.__dataPath__ + '/HistoryToRead'
        shutil.copyfile(his, hisData)
        return hisData

    def _loadBookmarkData_(self):
        bookmark = self.__dataPath__ + '/Bookmarks'
        with open(bookmark, 'r', encoding='UTF-8') as f:
            bookmarkData = json.load(f)
        return bookmarkData

    def _loadIconData_(self):
        cursor = sqlite3.connect(self._iconData_()).cursor()
        bitmapCursorResults = cursor.execute(
            'SELECT icon_id, image_data, width, height '
            'FROM favicon_bitmaps'
        ).fetchall()
        urlCursorResults = cursor.execute(
            'SELECT page_url, icon_id '
            'FROM icon_mapping'
        ).fetchall()
        cursor.close()
        return bitmapCursorResults, urlCursorResults

    def _loadHisData_(self):
        cursor = sqlite3.connect(self._hisData_()).cursor()
        hisInfoList = cursor.execute(
            'SELECT urls.url, urls.title, urls.last_visit_time '
            'FROM urls, visits '
            'WHERE urls.id = visits.url'
        ).fetchall()
        cursor.close()
        return hisInfoList

    def _iconInfo_(self):
        bitmapList, urlList = self._loadIconData_()
        bitmapInfoList = dict()
        for iconId, imageData, width, height in bitmapList:
            if iconId in bitmapInfoList.keys():
                if (
                        width < bitmapInfoList[iconId]['width']
                        or height < bitmapInfoList[iconId]['height']
                ):
                    continue
            bitmapInfoList.update(
                {
                    iconId: {
                        'imageData': imageData,
                        'width': width,
                        'height': height
                    }
                }
            )
        iconList = dict()
        for url, iconId in urlList:
            # netLocation = urlparse(url).netloc
            # print(url)
            # print(iconId)
            # print("=========")
            # print(netLocation)
            if url not in iconList.keys():
                iconList.update(
                    {
                        url: iconId
                    }
                )
        return bitmapInfoList, iconList

    def hisList(self):
        hisInfoList = self._loadHisData_()
        iconList = self.iconList
        hisList = list()
        items = list()
        for url, title, lastVisitTime in hisInfoList:
            item = url + title
            if item in items:
                itemIndex = items.index(item)
                if hisList[itemIndex]['lastVisitTime'] < lastVisitTime:
                    hisList[itemIndex]['lastVisitTime'] = lastVisitTime
            else:
                items.append(item)
                # netLocation = urlparse(url).netloc
                if url in iconList.keys():
                    iconId = iconList[url]
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
        hisList.sort(key=timeFromHisList, reverse=True)
        return hisList

    def bookmarkList(self):
        bookmarkList = list()
        data = self._loadBookmarkData_()
        iconList = self.iconList
        for root in data['roots']:
            try:
                childItems = data['roots'][root]['children']
            except Exception:
                continue
            bookmarkList = makeList(bookmarkList, childItems, root)

        for index in range(len(bookmarkList)):
            url = bookmarkList[index]['url']
            netLocation = urlparse(url).netloc
            if netLocation in iconList.keys():
                bookmarkList[index]['iconId'] = iconList[netLocation]
            else:
                bookmarkList[index]['iconId'] = 0
        return bookmarkList


class regexList:
    def __init__(self, queryString):
        queryStringLower = queryString.lower()
        queryList = queryStringLower.split()
        self.regexList = list()
        for query in queryList:
            # pattern = '.*?'.join(query)
            # regexList.append(re.compile(pattern))
            self.regexList.append(re.compile(query))

    def match(self, item):
        match = True
        for regex in self.regexList:
            match = regex.search(item) and match
        return match

class getHistory(Wox):
# class getHistory():
    cache = chromeCache()
    createIcon(cache.bitmapInfoList)
    hisList = cache.hisList()

    def query(self, queryString):
        hisList = self.hisList
        regex = regexList(queryString)
        result = list()
        for his in hisList:
            itemWithTime = his['item'] + stamp2time(his['lastVisitTime'], 'toMicroSec')
            if regex.match(itemWithTime.lower()):
                hisIndex = hisList.index(his)
                lastVisitTime = stamp2time(his['lastVisitTime'], 'toSec')
                url = his['url']
                if his['iconId'] != 0:
                    iconPath = './Images/iconId{}.png'.format(his['iconId'])
                else:
                    if(TargetPlatform == "Chrome"):
                        iconPath = './Images/chromeIcon.png'
                    elif(TargetPlatform == "Edge"):
                        iconPath = './Images/edgeIcon.png'
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
            if(TargetPlatform == "Chrome"):
                iconPath = './Images/chromeIcon.png'
            elif(TargetPlatform == "Edge"):
                iconPath = './Images/edgeIcon.png'
        lastVisitTime = stamp2time(his['lastVisitTime'], 'toMicroSec')
        results = [
            {
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
            }
        ]
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
