import os
import xbmcvfs
import xbmcgui
import xbmc
import xbmcaddon
import random
import codecs
import requests
from datetime import datetime, timedelta
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import xbmcvfs

__AddonID__ = 'plugin.video.annatel.tvvod'
__Addon__ = xbmcaddon.Addon(id=__AddonID__)
__AddonPath__ = xbmcvfs.translatePath(__Addon__.getAddonInfo('path'))
__AddonDataPath__ = os.path.join(xbmcvfs.translatePath(
    "special://userdata/addon_data"), __AddonID__)
__DefaultTitle__ = __Addon__.getAddonInfo('name')
__TempPath__ = os.path.join(__AddonDataPath__, "temp")

random.seed()


def CleanTempFolder():
    if (os.path.exists(__TempPath__)):
        for f in os.listdir(__TempPath__):
            tmpfile = os.path.join(__TempPath__, f)
            if (os.path.isfile(tmpfile)):
                os.remove(tmpfile)


def OpenSettings():
    __Addon__.openSettings(__AddonID__)


def ShowNotification(msg, duration, title=__DefaultTitle__, addon=None, sound=False):
    icon = None
    if (addon is not None):
        icon = addon.getAddonInfo('icon')
    dlg = xbmcgui.Dialog()
    dlg.notification(title, msg, icon, duration, sound)


def YesNoDialog(message,  heading=__DefaultTitle__, nolabel=None, yeslabel=None):
    dlg = xbmcgui.Dialog()
    response = dlg.yesno(heading, message, nolabel, yeslabel)
    return response


def DownloadFile(url, filePath):
    response = requests.get(url)

    # Create directory if it does not exist
    directory = os.path.dirname(filePath)

    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory structure created successfully! {directory}")

    if response.status_code == 200:
        # Open a file for writing and write the response content to it
        with open(filePath, 'wb+') as f:
            f.write(response.content)
    else:
        xbmc.log(
            f'Failed to download image. Status code: {response.status_code} link:{filePath}', level=xbmc.LOGERROR)


def ReadFile(file_path):
    text = None
    if (os.path.exists(file_path)):
        with codecs.open(file_path, "r", encoding='utf-8') as openFile:
            text = openFile.read()
    return text


def WriteFile(text, file_path, utf8=False):
    if (text is not None):
        local_dir = os.path.dirname(file_path)
        if (not os.path.exists(local_dir)):
            os.makedirs(local_dir)

        with codecs.open(file_path, "w+", encoding='utf-8') as openFile:
            openFile.write(text)

    else:
        DeleteFile(file_path)


def DeleteFile(file_path):
    if (os.path.exists(file_path)):
        os.remove(file_path)


def GetLogo(logo_name, default_logo='tv.png'):
    if ((logo_name is not None) and (len(logo_name) > 4)):
        filename = f"{logo_name}.png"
        full_filename = f'special://userdata/addon_data/{__AddonID__}/logos/{filename}'
        file_exists = (xbmcvfs.exists(full_filename)
                       or DownloadFile(f'http://client.annatel.tv/images/channels/{filename}', full_filename))
        xbmc.log(f'Logo: {full_filename} exists: {file_exists}',
                 level=xbmc.LOGINFO)
        if (file_exists):
            return full_filename
    return os.path.join(__AddonDataPath__,  default_logo)
