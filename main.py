# -*- coding: utf-8 -*-
# require pypiwin32, can be install by pip
from wox import Wox, WoxAPI
import os
import sqlite3
import shutil
import re
import webbrowser
import win32con
import win32clipboard as wincld
import time
import datetime


def stamp2time(timeStamp):
    baseDate = datetime.datetime(1601, 1, 1)
    yearSecond = timeStamp / 1000000
    us = timeStamp % 1000
    ms = (timeStamp % 1000000 - us) // 1000
    trueYearSecond = baseDate + datetime.timedelta(seconds=yearSecond, hours=8)
    toSecond = time.strftime('%Y-%m-%d %H:%M:%S', datetime.datetime.timetuple(trueYearSecond))
    tomSecond = toSecond + '.' + str(ms).zfill(3)
    touSecond = tomSecond + ' ' + str(us).zfill(3)
    return {
        'toSecond': toSecond,
        'tomSecond': tomSecond,
        'touSecond': touSecond,
        'trueYearSecond': trueYearSecond,
        'us': us,
        'ms': ms
    }


def getTimeFromHistoryList(historyList):
    return historyList['lastVisitTime']


class getHistory(Wox):
    # path to user's history database (Chrome)
    # and copy a read-only copy
    dataPath = r'C:\Users\WayneFerdon\AppData\Local\Google\Chrome\User Data\Default'
    shutil.copyfile(os.path.join(dataPath, 'History'), os.path.join(dataPath, 'History_2'))
    files = os.listdir(dataPath)

    historyDb = os.path.join(dataPath, 'History_2')

    # querying the db
    c = sqlite3.connect(historyDb)
    cursor = c.cursor()
    selectStatement = 'SELECT urls.url, urls.title, urls.last_visit_time FROM urls, visits WHERE urls.id = visits.url;'

    cursor.execute(selectStatement)
    cursorResults = cursor.fetchall()  # tuple
    historyList = []
    items = []
    for url, title, lastVisitTime in cursorResults:
        item = url + title
        if item in items:
            itemIndex = items.index(item)
            if historyList[itemIndex]['lastVisitTime'] < lastVisitTime:
                historyList[itemIndex]['lastVisitTime'] = lastVisitTime
            continue
        items.append(item)
        historyList.append(
            {
                'url': url,
                'title': title,
                'item': item,
                'lastVisitTime': lastVisitTime
            }
        )
    historyList.sort(key=getTimeFromHistoryList, reverse=True)

    def query(self, queryString):
        result = []
        historyList = self.historyList

        queryStringLower = queryString.lower()
        queryList = queryStringLower.split()
        regexList = []
        for query in queryList:
            # pattern = '.*?'.join(query)
            # regexList.append(re.compile(pattern))
            regexList.append(re.compile(query))

        for history in historyList:
            itemWithTime = history['item'] + stamp2time(history['lastVisitTime'])['touSecond']
            match = True
            for regex in regexList:
                match = regex.search(itemWithTime.lower()) and match
            if match:
                historyIndex = historyList.index(history)
                lastVisitTime = stamp2time(history['lastVisitTime'])
                toSecond = lastVisitTime['toSecond']
                result.append(
                    {
                        'Title': history['title'],
                        'SubTitle':  '[{}]'.format(toSecond) + history['url'],
                        'IcoPath': 'Images\chrome-logo.png',
                        'ContextData': historyIndex,
                        'JsonRPCAction': {
                            'method': 'openUrl',
                            'parameters': [history['url']],
                            'dontHideAfterAction': False,
                        }
                    }
                )
        return result

    def context_menu(self, historyIndex):
        history = self.historyList[historyIndex]
        url = history['url']
        title = history['title']
        logo = 'Images\chrome-logo.png'
        lastVisitTimeList = stamp2time(history['lastVisitTime'])
        lastVisitTime = lastVisitTimeList['touSecond']
        results = [{
            'Title': 'URL: ' + url,
            'SubTitle': 'Press Enter to Copy URL',
            'IcoPath': logo,
            'JsonRPCAction': {
                'method': 'copyData',
                'parameters': [url],
                'dontHideAfterAction': False,
            }
        }, {
            'Title': 'Title: ' + title,
            'SubTitle': 'Press Enter to Copy Title',
            'IcoPath': logo,
            'JsonRPCAction': {
                'method': 'copyData',
                'parameters': [title],
                'dontHideAfterAction': False,
            }
        }, {
            'Title': 'Last Visit Time: ' + lastVisitTime,
            'IcoPath': logo,
        }]
        return results

    def openUrl(self, url):
        webbrowser.open(url)

    def copyData(self, data):
        wincld.OpenClipboard()
        wincld.EmptyClipboard()
        wincld.SetClipboardData(win32con.CF_UNICODETEXT, data)
        wincld.CloseClipboard()


if __name__ == '__main__':
    getHistory()
