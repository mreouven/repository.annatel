import requests

import xbmc
import xbmcvfs
import xbmcaddon
import xbmcgui
import xbmcplugin
import sys
import os
import time
from urllib.parse import unquote
import pytz
from datetime import datetime, timedelta
import resources.lib.common as common

URL_TV_FEED = 'https://api-beta.annatel.tv/v1/tv/liveWithUrls'
URL_VOD_FEED = 'https://api-beta.annatel.tv/v1/epg/program'
URL_VOD_CATEGORIES = 'https://api-beta.annatel.tv/v1/epg/'
LOGIN_URL = "https://api-beta.annatel.tv/v1/auth/signin"
AddonID = 'plugin.video.annatel.tvvod'
Addon = xbmcaddon.Addon(AddonID)
AddonDataPath = os.path.join(xbmcvfs.translatePath(
    "special://userdata/addon_data"), AddonID)


class AnnatelTv:
    token = None

    def __init__(self) -> None:
        self.GetCredentials()

    def GetCredentials(self):
        self.username = Addon.getSetting('username')
        self.password = Addon.getSetting('password')

    def IsLoggedIn(self):
        return ((self.username is not None) and (self.username != "") and (self.password is not None) and (self.password != ""))

    def GetToken(self):
        if(self.token is not None and self.dateToken is not None and (datetime.now() - self.dateToken) < timedelta(hours=1)):
            return self.token
        payload = {
            'login': self.username,
            'password': self.password,
            'rememberMe': 0
        }
        response = requests.request("POST", LOGIN_URL, data=payload)
        if response.status_code == 200 and response.json()['code'] == 'OK':
            self.token = response.json()['data']['token']
            self.dateToken = datetime.now()
            return response.json()['data']['token']

        raise Exception('Credentials are not valid')

    def GetHeaders(self):
        token = self.GetToken()
        headers = {
            'Authorization': 'Bearer ' + token
        }
        return headers

    def GetRelavantChannels(self):
        try:
            url = URL_TV_FEED
            headers = self.GetHeaders()
            response = requests.request(
                "GET", url, headers=headers)
            xbmc.log("TV channels loading", level=xbmc.LOGINFO)
            if response.status_code == 200 and response.json()['code'] == 'OK':

                relevant = filter(
                    lambda x: x['replay_url'] is not None,    response.json()['data'])
                return list(map(lambda x: {
                    'name': x['name'],
                    'url': x['replay_url'],
                    'id': x['uid'],
                    'logo': x['css_class']
                }, relevant))

            raise Exception('Error while getting TV channels')
        except Exception as e:
            common.ShowNotification(
                "Error while getting vod: " + str(e), 10, addon=Addon)
            xbmc.log(str(e), level=xbmc.LOGERROR)

    def GetCategories(self):
        try:
            url = URL_VOD_CATEGORIES+'categories'
            headers = self.GetHeaders()
            response = requests.request("GET", url, headers=headers)
            xbmc.log("VOD categories loading", level=xbmc.LOGINFO)
            if response.status_code == 200 and response.json()['code'] == 'OK':
                return response.json()['data']

            raise Exception('Error while getting VOD categories')
        except Exception as e:
            common.ShowNotification(
                "Error while getting vod: " + str(e), 10, addon=Addon)
            xbmc.log(str(e), level=xbmc.LOGERROR)

    def GetProgramByDate(self, channel_id, date):
        url = URL_VOD_CATEGORIES+'program'
        headers = self.GetHeaders()
        params = {
            'uid': channel_id,
            'date': date
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200 and response.json()['code'] == 'OK':
            return self.parseItemsResult(response.json()['data'], 'byChannel')

    def GetCategoryItems(self, current_category):
        url = URL_VOD_CATEGORIES+'category'
        headers = self.GetHeaders()
        end_date = int(time.time())
        params = {
            'category': unquote(current_category).replace('+', ' '),
            'end': end_date,
            'start': end_date - (7 * 24 * 60 * 60)
        }
        xbmc.log(str(params), level=xbmc.LOGINFO)
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200 and response.json()['code'] == 'OK':
            return self.parseItemsResult(response.json()['data'], current_category)

    def Search(self, search_term):
        url = URL_VOD_CATEGORIES+'search'
        headers = self.GetHeaders()
        end_date = int(time.time())
        params = {
            'query': search_term,
            'end': end_date,
            'start': end_date - (7 * 24 * 60 * 60),
            'limit': 100
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200 and response.json()['code'] == 'OK':
            return self.parseItemsResult(response.json()['data'], 'search')

    def parseItemsResult(self, items, current_category):
        result = list(map(lambda x: {
            'name': self.TitleItem(x, current_category),
            'id': x['id'],
            'description': x['description'],
            'image': x['image'],
        }, items))
        unique_values = list(
            {item['name']: item for item in result}.values())
        return unique_values

    def GetVideoURL(self, id):
        xbmc.log("get data for id: "+str(id), level=xbmc.LOGINFO)
        url = 'https://api-beta.annatel.tv/v1/replay/program/' + id
        headers = self.GetHeaders()
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and response.json()['code'] == 'OK':
            return response.json()['data']

    def TitleItem(self, item, category):
        tz = pytz.timezone('Asia/Jerusalem')
        if category == 'film' or category == 'research':
            return item['title']
        elif category == 'byChannel':
            start_date = datetime.fromisoformat(
                item['startDate']).astimezone(tz)
            formatted_date_str = start_date.strftime("%H:%M")
            return f'{formatted_date_str} - {item["title"]}'
        else:
            start_date = datetime.fromisoformat(
                item['startDate']).astimezone(tz)
            formatted_date_str = start_date.strftime("%d/%m %y:%H:%M")
            return f'{item["title"]}   -- {formatted_date_str} ({item["xmltv_id"].split(".")[0].capitalize()})'
