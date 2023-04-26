import xbmc
import xbmcaddon
import traceback
import xbmcvfs
import os
import resources.lib.common as common
import xml.etree.ElementTree as ET


__AddonID__ = 'plugin.video.annatel.tv'
__Addon__ = xbmcaddon.Addon(__AddonID__)
__IPTVSimple__AddonDataPath____ = os.path.join(xbmcvfs.translatePath(
    "special://userdata/addon_data"), "pvr.iptvsimple")
__AddonDataPath__ = os.path.join(xbmcvfs.translatePath(
    "special://userdata/addon_data"), __AddonID__)


if (not os.path.exists(__AddonDataPath__)):
    os.makedirs(__AddonDataPath__)


def GetIptvAddon(show_message=False):
    iptvAddon = None

    if os.path.exists(xbmcvfs.translatePath("special://home/addons/") + 'pvr.iptvsimple') or os.path.exists(xbmcvfs.translatePath("special://xbmc/addons/") + 'pvr.iptvsimple'):
        try:
            iptvAddon = xbmcaddon.Addon("pvr.iptvsimple")
        except:
            print("---- Annatel ----\nIPTVSimple addon is disable.")
            msg1 = "PVR IPTVSimple is Disable."
            msg2 = "Please enable IPTVSimple addon."
    else:
        msg1 = "PVR IPTVSimple is NOT installed on your machine."
        msg2 = "Please install XBMC version that include IPTVSimple in it."

    if ((iptvAddon is None) and (show_message)):
        common.OKmsg(msg1, msg2)

    return iptvAddon


def RefreshIPTVlinks(channel_list):
    iptvAddon = GetIptvAddon()
    if (iptvAddon is None):
        return False

    common.ShowNotification("Updating links...", 300000, addon=__Addon__)

    try:
        finalM3Ulist = MakeM3U(channel_list)
        # The final m3u file location.
        finalM3Ufilename = os.path.join(__AddonDataPath__, 'iptv.m3u')
        current_file = common.ReadFile(finalM3Ufilename)
        xbmc.log(
            f"---- Annatel ----\nIPTVSimple: M3U file is updated.{finalM3Ufilename}", level=xbmc.LOGINFO)
        if ((current_file is None) or (finalM3Ulist != current_file)):
            common.WriteFile(finalM3Ulist, finalM3Ufilename, utf8=True)

            UpdateIPTVSimpleSettings(iptvAddon, restart_pvr=True)
        else:
            UpdateIPTVSimpleSettings(iptvAddon, restart_pvr=False)
    except Exception as e:
        traceback.print_exc()
        common.ShowNotification("Error: {0}".format(e), 5000, addon=__Addon__)
        xbmc.log("---- Annatel ----\nError: {0}".format(str(e)), xbmc.LOGERROR)
        return False
    # DeleteCache()
    common.ShowNotification("Updating is done.", 2000, addon=__Addon__)
    return True


def MakeM3U(list, is_logo_extension=True):
    M3Ulist = []
    M3Ulist.append("#EXTM3U\n")

    for item in list:
        tvg_logo = GetLogo(item.tvg_logo, is_logo_extension)
        M3Ulist.append(item.GetM3uLine(tvg_logo))

    return "\n".join(M3Ulist)


def DeleteCache():
    iptvsimple_path = __IPTVSimple__AddonDataPath____
    if (os.path.exists(iptvsimple_path)):
        for f in os.listdir(iptvsimple_path):
            if (os.path.isfile(os.path.join(iptvsimple_path, f))):
                if (f.endswith('cache')):
                    os.remove(os.path.join(iptvsimple_path, f))


def UpdateIPTVSimpleSettings(iptvAddon=None, restart_pvr=False):
    if (iptvAddon is None):
        iptvAddon = GetIptvAddon()
        if (iptvAddon is None):
            return

    iptvSettingsFile = os.path.join(
        __IPTVSimple__AddonDataPath____, "instance-settings-1.xml")
    xbmc.log(
        f"---- Annatel ----\nIPTVSimple: Settings file.{iptvSettingsFile}", level=xbmc.LOGINFO)
    if (not os.path.isfile(iptvSettingsFile)):
        # make 'settings.xml' in 'userdata/addon_data/pvr.iptvsimple' folder
        iptvAddon.setSetting("epgPathType", "0")

    # get settings.xml into dictionary
    tree = ReadSettings(iptvSettingsFile)

    newDictionary = {
        "epgPathType": "0",
        "epgPath": os.path.join(__AddonDataPath__, 'epg.xml'),
        "logoPathType": "0",
        "logoPath": os.path.join(__AddonDataPath__, 'logos'),
        "m3uPathType": "0",
        "m3uPath": os.path.join(__AddonDataPath__, 'iptv.m3u'),
        "kodi_addon_instance_name": "Annatel",
    }
    ReplaceSetting(newDictionary, tree=tree, path=iptvSettingsFile)
    if (restart_pvr == True):
        RefreshIPTVSimple()


def RefreshIPTVSimple():
    xbmc.executebuiltin('StartPVRManager')


def ReadSettings(source):
    tree = ET.parse(source)
    # elements = tree.findall('*')

    # settingsDictionary = {}
    # for elem in elements:
    #     settingsDictionary[elem.get('id')] = {'value': elem.get(
    #         'value'), 'default': elem.get('default')}

    return tree


def ReplaceSetting(newDictionary, tree, path):
    for k, v in newDictionary.items():
        for elem in tree.iter():
            if (elem.get('id') == k):
                elem.text = v
                if 'default' in elem.attrib:
                    elem.attrib.pop('default')
                break
    tree.write(path)


def replaceEpgFile(epg_data):
    finalEpgFile = os.path.join(__AddonDataPath__, 'epg.xml')
    common.WriteFile(epg_data, finalEpgFile)


def GetLogo(link, is_logo_extension):
    if ((link is not None) and (len(link) > 4)):
        filename = link.split("/")[-1]
        full_filename = os.path.join(__AddonDataPath__, 'logos', filename)
        file_exists = (os.path.exists(full_filename)
                       or common.DownloadFile(link, full_filename))

        if (file_exists):
            if (is_logo_extension):
                return filename
            else:
                return filename[:-4]
        else:
            return ""
    else:
        return ""
