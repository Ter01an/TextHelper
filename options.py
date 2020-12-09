import wx


class Options(wx.Dialog):

    def __init__(self):
        self.REPLACE = False
        self.DEBUG = False
        self.GENDER = 'auto'

        wx.Dialog.__init__(self, None, title="Настройки", style=wx.STAY_ON_TOP)

        text_sizer = wx.BoxSizer(wx.VERTICAL)
        text_before_1 = wx.StaticText(self, label="Укажите кто ведет повествование:")
        text_before_1.SetFont(wx.Font(14, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        text_before_2 = wx.StaticText(self, label="Пример:")
        text_before_3 = wx.StaticText(self, label="До: Я подошел к Ване. Я его ударил.")

        text_sizer.Add(text_before_1, 0, wx.ALL, 5)
        text_sizer.Add(text_before_2, 0, wx.ALL, 5)
        text_sizer.Add(text_before_3, 0, wx.ALL, 5)

        text_after_sizer = wx.BoxSizer(wx.HORIZONTAL)
        text_after_1 = wx.StaticText(self, label="После: ")
        text_after_2 = wx.StaticText(self, label="Он")
        text_after_2.SetBackgroundColour(wx.Colour(254, 228, 90))
        text_after_3 = wx.StaticText(self, label=" подошел к Ване. ")
        text_after_4 = wx.StaticText(self, label="Потерпевший")
        text_after_4.SetBackgroundColour(wx.Colour(254, 228, 90))
        text_after_5 = wx.StaticText(self, label=" его ударил.")

        text_after_sizer.Add(text_after_1, 0, wx.ALL, 0)
        text_after_sizer.Add(text_after_2, 0, wx.ALL, 0)
        text_after_sizer.Add(text_after_3, 0, wx.ALL, 0)
        text_after_sizer.Add(text_after_4, 0, wx.ALL, 0)
        text_after_sizer.Add(text_after_5, 0, wx.ALL, 0)

        text_sizer.Add(text_after_sizer, 0, wx.ALL, 5)

        settings_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.gender = wx.RadioBox(self, label="Род:", choices=['Авто', 'Мужской', 'Женский'])
        self.gender.Bind(wx.EVT_RADIOBOX, self.onRadioBox)

        self.debug = wx.CheckBox(self, label="Подсветка")
        self.debug.Bind(wx.EVT_CHECKBOX, self.onCheckBox)

        settings_sizer.Add(self.gender, 0, wx.ALL, 5)
        settings_sizer.Add(self.debug, 0, wx.ALL, 5)

        replace_sizer = wx.BoxSizer(wx.HORIZONTAL)

        replace_lbl = wx.StaticText(self, label="Обозначение лица:")
        replace_sizer.Add(replace_lbl, 0, wx.ALL | wx.CENTER, 5)

        self.replace = wx.TextCtrl(self, value="Потерпевший")
        replace_sizer.Add(self.replace, 0, wx.ALL, 5)

        self.btnAccept = wx.Button(self, label="Применить")
        replace_sizer.Add(self.btnAccept, 0, wx.ALL, 5)

        self.btnClose = wx.Button(self, label="Отмена")
        replace_sizer.Add(self.btnClose, 0, wx.ALL, 5)

        self.Bind(wx.EVT_BUTTON, self.onAccept, id=self.btnAccept.GetId())
        self.Bind(wx.EVT_BUTTON, self.onClose, id=self.btnClose.GetId())
        # self.Bind(wx.EVT_CHAR_HOOK, self.onKey)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(text_sizer, 0, wx.ALL, 5)
        main_sizer.Add(settings_sizer, 0, wx.ALL, 5)
        main_sizer.Add(replace_sizer, 0, wx.ALL, 5)

        # self.SetSize((420, 170))
        self.SetSizerAndFit(main_sizer)

    def onCheckBox(self, event):
        if self.debug.IsChecked():
            self.DEBUG = True
        else:
            self.DEBUG = False

    def onRadioBox(self, event):
        selected = self.gender.GetStringSelection()
        if selected == "Авто":
            self.GENDER = 'auto'
        if selected == "Мужской":
            self.GENDER = 'masc'
        if selected == "Женский":
            self.GENDER = 'femn'

    def onKey(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN or event.GetKeyCode() == wx.WXK_NUMPAD_ENTER:
            self.REPLACE = self.replace.GetValue()
            wx.CallAfter(self.Destroy)
            self.Close()

    def onAccept(self, event):
        self.REPLACE = self.replace.GetValue()
        wx.CallAfter(self.Destroy)
        self.Close()

    def onClose(self, event):
        wx.CallAfter(self.Destroy)
        self.Close()
