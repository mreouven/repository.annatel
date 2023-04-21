import resources.lib.myIPTVSimple as myIPTVSimple
from resources.lib.annatel import AnnatelTv, LoadLogin
import resources.lib.common as common
from typing import List
import threading
import sys
import os
import xbmcaddon
import xbmc
from resources.lib.epgParser import EpgParser
import traceback

UpdateInterval = 4 * 3600  # 4 hours
LoginInterval = 5  # 5 seconds
RetryInterval = 5 * 60  # 5 minutes
WaitInterval = 5  # 5 seconds


tvThread: threading.Thread | None = None
tvCounter: int = 0

UpdateInterval = 4 * 3600  # 4 hours
LoginInterval = 5  # 5 seconds
RetryInterval = 5 * 60  # 5 minutes
WaitInterval = 5  # 5 seconds

tvThread: threading.Thread | None = None
tvCounter: int = 0

annatel = AnnatelTv()


def OnLoad() -> None:
    # try:
    #     import pydevd  # with the addon script.module.pydevd, only use `import pydevd`
    #     pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
    # except ImportError:
    #     sys.stderr.write(
    #         "Error: " + "You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")

    global tvCounter
    global tvThread
    try:
        common.CleanTempFolder()
    except:
        pass
    if not annatel.IsLoggedIn():
        LoadLogin()
    else:
        tvCounter = 0
        myIPTVSimple.GetIptvAddon(show_message=True)
        CheckUpdates()


def OnExit() -> None:
    global tvThread
    if tvThread is not None:
        tvThread.join()
        tvThread = None


def SleepFor(time_period: int) -> None:
    while not xbmc.Monitor().abortRequested() and time_period > 0:
        xbmc.sleep(1000)
        time_period -= 1


def CheckUpdates() -> None:
    global tvCounter
    global tvThread
    status = not xbmc.Monitor().abortRequested() and annatel.IsLoggedIn(
    ) and myIPTVSimple.GetIptvAddon() is not None
    while status:
        tvCounter -= WaitInterval
        if tvCounter <= 0 and tvThread is None:
            tvCounter = UpdateInterval
            tvThread = threading.Thread(target=UpdateTVChannels).start()
        xbmc.sleep(WaitInterval * 1000)


def UpdateTVChannels() -> None:
    global tvCounter
    global tvThread
    result = False
    try:
        common.ShowNotification("Get tv channel", 10)
        channels_list = annatel.GetTVChannels()
        if channels_list is not None:
            myIPTVSimple.RefreshIPTVlinks(channels_list)
            # UpdateEpg(list(map(lambda x: x.uid, channels_list)))

    except Exception as e:
        xbmc.log("Error: " + str(e), level=xbmc.LOGERROR)
        traceback.print_exc()
        result = False
    if result:
        tvCounter = UpdateInterval
    else:
        tvCounter = RetryInterval
        tvThread = None


def UpdateEpg(channel_list) -> None:
    try:
        common.ShowNotification("Update epg", 10)
        epgParser = EpgParser(token=annatel.GetToken(),
                              channels_ids=channel_list)
        data = epgParser.getChannelsData()
        myIPTVSimple.replaceEpgFile(data)
        common.ShowNotification("Update epg success", 10)

    except Exception as e:
        xbmc.log("Error: " + str(e), level=xbmc.LOGERROR)
        traceback.print_exc()


OnLoad()
while not xbmc.Monitor().abortRequested():
    if annatel.IsLoggedIn() and myIPTVSimple.GetIptvAddon() is not None:
        CheckUpdates()
    else:
        SleepFor(LoginInterval)
        OnExit()
