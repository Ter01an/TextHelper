# -*- coding: utf8 -*-

import wx
import wx.adv
import inc


def CreateMenuItem(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item


class TaskBarIcon(wx.adv.TaskBarIcon):

    def __init__(self, frame):
        wx.adv.TaskBarIcon.__init__(self)
        self.frame = frame

        icon = wx.Icon(inc.resource_path('./icon.ico'), wx.BITMAP_TYPE_ICO)

        self.SetIcon(icon, "Текстовый помощник")

    def CreatePopupMenu(self):
        menu = wx.Menu()
        CreateMenuItem(menu, 'Выход', self.Exit)
        return menu

    def Exit(self, event):
        wx.CallAfter(self.Destroy)
        self.frame.Close()
