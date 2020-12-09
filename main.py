import wx
import tray
import clipboard
import converter
import time
import os
from options import Options


class MainFrame(wx.Frame):

    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.tbIcon = tray.TaskBarIcon(self)

        self.hotKeyId = 100
        self.RegisterHotKey(self.hotKeyId, wx.MOD_CONTROL, wx.WXK_F11)
        self.Bind(wx.EVT_HOTKEY, self.handleConvert, id=self.hotKeyId)
        self.convert = converter.Converter()

    def handleConvert(self, event):
        dlg = Options()
        if os.name == 'nt':
            from win32gui import GetForegroundWindow, SetForegroundWindow

            aw = (GetForegroundWindow())

            dlg.CenterOnScreen()
            dlg.ShowModal()

            SetForegroundWindow(aw)

        time.sleep(.3)

        if dlg.REPLACE:
            buffer = clipboard.copy()

            self.convert.setReplacer(dlg.REPLACE)
            self.convert.setGender(dlg.GENDER)
            buffer_new = self.convert.Process(buffer, dlg.DEBUG)

            clipboard.past(buffer_new[0], buffer_new[1])


def main():
    app = wx.App(redirect=False)
    MainFrame(None, wx.ID_ANY, "Текстовый помощник")
    app.MainLoop()


if __name__ == "__main__":
    main()
