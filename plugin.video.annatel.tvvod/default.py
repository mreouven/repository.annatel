import xbmcgui
import xbmcaddon
import xbmc
import xbmcplugin
import sys
import os
import urllib
from xml.dom.minidom import parse
from resources.lib.annatel import AnnatelTv
from resources.lib.common import GetLogo
from urllib.parse import parse_qs
import datetime


__settings__ = xbmcaddon.Addon(id='plugin.video.annatel.tvvod')
__language__ = __settings__.getLocalizedString


username = __settings__.getSetting('username')
password = __settings__.getSetting('password')

annatel = AnnatelTv()


LNK_PATH = os.path.join(__settings__.getAddonInfo(
    'path'), 'resources', 'box.lnk')


class AnnatelTVVod:
    """
    main plugin class
    """
    debug_mode = True  # Debug mode

    def __init__(self, *args, **kwargs):
        params = self.get_params()
        channel = None
        date = None
        mode = None
        ID = None
        try:
            channel = urllib.parse.quote_plus(params["channel"])
        except Exception as e:
            xbmc.log("Error: "+str(e), level=xbmc.LOGERROR)
            pass
        try:
            date = urllib.parse.quote_plus(params["date"])
        except Exception as e:
            xbmc.log("Error: "+str(e), level=xbmc.LOGERROR)
            pass
        try:
            mode = int(params["mode"])
        except Exception as e:
            xbmc.log("Error: "+str(e), level=xbmc.LOGERROR)
            pass
        try:
            ID = int(params["id"])
        except Exception as e:
            xbmc.log("Error: "+str(e), level=xbmc.LOGERROR)
            pass

        if self.debug_mode:
            xbmc.log("Mode: "+str(mode), level=xbmc.LOGINFO)
            xbmc.log("Channel: "+str(channel), level=xbmc.LOGINFO)
            xbmc.log("Date: "+str(date), level=xbmc.LOGINFO)
            xbmc.log("ID: "+str(ID), level=xbmc.LOGINFO)

        if ID is not None:
            xbmc.log("running id: "+str(ID), level=xbmc.LOGINFO)
            self.play(ID)
        elif mode == None:
            self.initialstate()
            self.updateDir()

        elif mode == 1:
            self.GET_CHANNELS()
            self.updateDir()

        elif mode == 2:
            self.GET_DATES(channel)
            self.updateDir()

        elif mode == 3:
            self.GET_PROGRAMS(channel, date)
            self.updateDir()

        elif mode == 4:
            self.GET_CATEGORIES()
            self.updateDir()

        elif mode == 5:
            self.GET_CATEGORY(channel)
            self.updateDir()
        elif mode == 10:
            self.SEARCH()
            self.updateDir()

        else:
            xbmc.log("Error: no ", level=xbmc.LOGERROR)

    def updateDir(self):
        xbmcplugin.setPluginCategory(handle=int(
            sys.argv[1]), category=__language__(30000))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        xbmcplugin.addSortMethod(handle=int(
            sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(handle=int(
            sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_LABEL)

    def initialstate(self):
        self.addDir('Chaines', "", "", 1,
                    'replay.png')
        self.addDir('Catégories', "", "", 4, "DefaultGenre.png")
        self.addDir('Chercher', "", "", 10, 'DefaultAddonsSearch.png')

    def GET_CHANNELS(self):
        channels = annatel.GetRelavantChannels()
        for channel in channels:
            self.addDir(channel['name'], channel['id'], "",
                        2, GetLogo(channel['logo']))

    def GET_DATES(self, channel):
        start_date = datetime.date.today() + datetime.timedelta(days=-7)
        # Define the weekday names and month names in French
        weekday_names = ['lundi', 'mardi', 'mercredi',
                         'jeudi', 'vendredi', 'samedi', 'dimanche']
        month_names = ['', 'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                       'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']

        for i in reversed(range(7)):
            date = start_date + datetime.timedelta(days=i+1)
            weekday = weekday_names[date.weekday()]
            month = month_names[date.month]
            day = date.day
            year = date.year
            date_str = f"{weekday} {day} {month} {year}"
            self.addDir(date_str, channel,
                        f"{year}-{date.month}-{date.day}", 3, "annees.png")

    def GET_PROGRAMS(self, channel, date):
        programs = annatel.GetProgramByDate(channel, date)
        for program in programs:
            self.addVideo(program['name'], program['id'],
                          program['description'], program['image'])

    def GET_CATEGORIES(self):
        categories = annatel.GetCategories()
        for category in categories:
            self.addDir(category.capitalize(), category,
                        "", 5, "DefaultCountry.png")

    def GET_CATEGORY(self, channel):
        categories = annatel.GetCategoryItems(channel)
        for category in categories:
            self.addVideo(category['name'], category['id'],
                          category['description'], category['image'])

    def SEARCH(self):
        keyboard = xbmc.Keyboard('', 'Rechercher un titre')
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            query = keyboard.getText()
            programs = annatel.Search(query)
            for program in programs:
                self.addVideo(program['name'], program['id'],
                              program['description'], program['image'])

    def addDir(self, name, channel, date, mode, iconimage):
        if 'Default' not in iconimage and 'special' not in iconimage:
            iconimage = 'special://home/addons/plugin.video.annatel.tvvod/resources/art/'+iconimage
        u = sys.argv[0]+"?channel="+urllib.parse.quote_plus(
            str(channel).encode('utf-8'))+"&mode="+str(mode)+"&date="+urllib.parse.quote_plus(str(date).encode('utf-8'))
        liz = xbmcgui.ListItem(
            name)
        liz.setInfo("video", {"title": name})
        liz.setArt(
            {'icon': iconimage})
        ok = xbmcplugin.addDirectoryItem(handle=int(
            sys.argv[1]), url=u, listitem=liz, isFolder=True)
        return ok

    def addVideo(selt, name, id, description, image='DefaultVideo.png'):
        u = sys.argv[0]+"?id="+urllib.parse.quote_plus(str(id).encode('utf-8'))
        liz = xbmcgui.ListItem(name, name)
        liz.setArt(
            {'icon': 'DefaultVideo.png', 'thumb': image, 'poster': image, 'banner': image})
        liz.setInfo("video", {"Title": name,
                    "Label": name, "Plot": description})

        xbmcplugin.addDirectoryItem(handle=int(
            sys.argv[1]), url=u, listitem=liz, isFolder=True)

    def play(self, id):
        data = annatel.GetVideoURL(str(id))
        listitem = xbmcgui.ListItem()
        listitem.setArt(
            {'icon': 'DefaultVideo.png', 'thumb': data['image'], 'poster': data['image'], 'banner': data['image']})
        listitem.setInfo(
            'video', {'Title': data['title'], 'Genre': data['category'], 'plot': data['description'], 'thumb': data['image']})
        xbmc.Player().play(data['url'], listitem)

    def get_params(self):
        paramstring = sys.argv[2]

        if len(paramstring) >= 2:
            params = sys.argv[2]
            cleanedparams = params.replace('?', '')
            query_params = parse_qs(cleanedparams)
            query_dict = {k: v[0] if len(
                v) == 1 else v for k, v in query_params.items()}
            return query_dict


if __name__ == '__main__':
    if username == '' or password == '':
        resp = xbmcgui.Dialog().yesno("Authentification",
                                      "Il faut configurer votre login et mot de passe Annatel TV!\nCliquez sur Yes pour configurer votre login et mot de passe")
        if resp:
            respLogin = __settings__.openSettings()
            if respLogin:
                username = __settings__.getSetting('username')
                password = __settings__.getSetting('password')
            else:
                xbmc.executebuiltin(
                    'XBMC.Notification("Authentification","Merci d\'entrer votre login et mot de passe Annatel TV", 5000)')
        else:
            xbmc.executebuiltin(
                'XBMC.Notification("Authentification","Merci d\'entrer votre login et mot de passe Annatel TV", 10000)')

    username = __settings__.getSetting('username')
    password = __settings__.getSetting('password')
    if username != '' and password != '':
        AnnatelTVVod()
