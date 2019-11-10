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


def stamp2time(timeStamp):
    baseDate = datetime.datetime(1601, 1, 1)
    yearSecond = timeStamp / 1000000
    microSecond = timeStamp % 1000
    milliSecond = (timeStamp % 1000000 - microSecond) // 1000
    trueYearSecond = baseDate + datetime.timedelta(seconds=yearSecond, hours=8)
    toSecond = time.strftime('%Y-%m-%d %H:%M:%S', datetime.datetime.timetuple(trueYearSecond))
    toMilliSecond = toSecond + '.' + str(milliSecond).zfill(3)
    toMicroSecond = toMilliSecond + ' ' + str(microSecond).zfill(3)
    return {
        'toSecond': toSecond,
        'toMilliSecond': toMilliSecond,
        'toMicroSecond': toMicroSecond,
        'trueYearSecond': trueYearSecond,
        'microSecond': microSecond,
        'milliSecond': milliSecond
    }


def getTimeFromHistoryList(historyList):
    return historyList['lastVisitTime']


class getHistory(Wox):
    # path to user's history database (Chrome) and copy a read-only copy
    # default path is C:/Users/[UserName]/AppData/Local/Google/User Data/Default/History
    localAppData = os.environ['localAppData'.upper()]
    dataPath = localAppData + '/Google/Chrome/User Data/Default'
    history = dataPath + '/History'
    historyToRead = dataPath + '/HistoryToRead'
    shutil.copyfile(history, historyToRead)

    # querying the db
    connection = sqlite3.connect(historyToRead)
    cursor = connection.cursor()
    selectStatement = 'SELECT urls.url, urls.title, urls.last_visit_time FROM urls, visits WHERE urls.id = visits.url'

    cursor.execute(selectStatement)
    cursorResults = cursor.fetchall()
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
            itemWithTime = history['item'] + stamp2time(history['lastVisitTime'])['toMicroSecond']
            match = True
            for regex in regexList:
                match = regex.search(itemWithTime.lower()) and match
            if match:
                historyIndex = historyList.index(history)
                lastVisitTime = stamp2time(history['lastVisitTime'])
                toSecond = lastVisitTime['toSecond']
                url = history['url']
                result.append(
                    {
                        'Title': history['title'],
                        'SubTitle': '[{time}]{url}'.format(time=toSecond, url=url),
                        'IcoPath': './Images/chromeIcon.png',
                        'ContextData': historyIndex,
                        'JsonRPCAction': {
                            'method': 'openUrl',
                            'parameters': [url],
                            "dontHideAfterAction": False
                        }
                    }
                )
        return result

    def context_menu(self, historyIndex):
        history = self.historyList[historyIndex]
        url = history['url']
        title = history['title']
        logo = './Images/chromeIcon.png'
        lastVisitTimeList = stamp2time(history['lastVisitTime'])
        lastVisitTime = lastVisitTimeList['toMicroSecond']
        results = [{
            'Title': 'URL: ' + url,
            'SubTitle': 'Press Enter to Copy URL',
            'IcoPath': logo,
            'JsonRPCAction': {
                'method': 'copyData',
                'parameters': [url],
                "dontHideAfterAction": False
            }
        }, {
            'Title': 'Title: ' + title,
            'SubTitle': 'Press Enter to Copy Title',
            'IcoPath': logo,
            'JsonRPCAction': {
                'method': 'copyData',
                'parameters': [title],
                "dontHideAfterAction": False
            }
        }, {
            'Title': 'Last Visit Time: ' + lastVisitTime,
            'SubTitle': 'Press Enter to Copy Last Visit Time',
            'IcoPath': logo,
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
