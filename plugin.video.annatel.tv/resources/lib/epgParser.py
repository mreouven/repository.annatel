import xbmc
import xbmcaddon
import resources.lib.common as common
import requests
from datetime import datetime

import traceback

__AddonID__ = 'plugin.video.annatel.tv'
__Addon__ = xbmcaddon.Addon(__AddonID__)
_EGPURL_ = 'https://api-beta.annatel.tv/v1/epg/program'


class EpgParser:
    def __init__(self, token: str, channels_ids: list):
        self.token = token
        self.channels_ids = channels_ids

    def getChannelsData(self):
        channels_data = []
        xbmc.log("---- Annatel ----\nGetting EPG data", xbmc.LOGINFO)
        current_date = datetime.now()
        formatted_date = current_date.strftime('%Y-%m-%d')
        for channel_id in self.channels_ids:
            channels_data.extend(self.GetProgramByDate(
                channel_id, formatted_date))

        return self.parseEpg(channels_data)

    def generateHeader(self):
        return f'''<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE tv SYSTEM "xmltv.dtd">
        <tv>'''

    def generateChannel(self, xmltv_id):
        return f'''<channel id="{xmltv_id}">
             <display-name>{xmltv_id.split('.')[0]}</display-name>
        </channel>'''

    def generateProgramme(self, channel):
        start = datetime.utcfromtimestamp(
            channel['start']).strftime('%Y%m%d%H%M%S +0300')
        stop = datetime.utcfromtimestamp(
            channel['stop']).strftime('%Y%m%d%H%M%S +0300')
        return f'''<programme start="{start}" stop="{stop}" channel="{channel['xmltv_id']}">
        <title lang="en">{channel['title']}</title>
            <desc lang="en">{channel['description']}</desc>
            <image type="poster" size="1" orient="P" system="tvdb">{channel['image']}</image>
            <category lang="en">{channel['category']}</category>
        </programme>'''

    def parseEpg(self, channels):
        try:
            epg = []
            epg.append(self.generateHeader())

            epg.extend(list(map(lambda x: self.generateChannel(x), set(
                map(lambda channel: channel['xmltv_id'], channels)))))
            epg.extend(list(map(lambda x: self.generateProgramme(x), channels)))
            epg.append('\n</tv>')
            return '\n'.join(epg).replace('\r', '')
        except Exception as e:
            xbmc.log(f"---- Annatel ----\nError: {str(e)}", xbmc.LOGERROR)
            traceback.print_exc()

    def GetHeaders(self):
        headers = {
            'Authorization': 'Bearer ' + self.token
        }
        return headers

    def GetProgramByDate(self, channel_id, date):
        headers = self.GetHeaders()
        params = {
            'uid': channel_id,
            'date': date
        }
        response = requests.get(_EGPURL_, headers=headers, params=params)
        if response.status_code == 200 and response.json()['code'] == 'OK':
            return response.json()['data']
