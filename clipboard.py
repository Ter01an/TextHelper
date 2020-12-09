import klembord
import time
import os
from pynput.keyboard import Key, Controller

keyboard = Controller()


def copy():
    if os.name == 'nt':
        import win32clipboard
        win32clipboard.OpenClipboard(0)
        win32clipboard.EmptyClipboard()
        win32clipboard.CloseClipboard()
        time.sleep(.1)

        __ctrl_c()
        time.sleep(.1)

        win32clipboard.OpenClipboard(0)

        if not win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
            text = ""
        else:
            text = win32clipboard.GetClipboardData()

        if not win32clipboard.IsClipboardFormatAvailable(win32clipboard.RegisterClipboardFormat("HTML Format")):
            html = ""
        else:
            html = win32clipboard.GetClipboardData(win32clipboard.RegisterClipboardFormat("HTML Format")).decode('utf-8')

        if not win32clipboard.IsClipboardFormatAvailable(win32clipboard.RegisterClipboardFormat('Rich Text Format')):
            rtf = ""
        else:
            rtf = win32clipboard.GetClipboardData(win32clipboard.RegisterClipboardFormat('Rich Text Format'))

        win32clipboard.CloseClipboard()

        return text, html, rtf


def past(text, html=None, rtf=None):
    if os.name == 'nt':
        import win32clipboard
        win32clipboard.OpenClipboard(0)
        win32clipboard.EmptyClipboard()

        if text:
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        if html:
            win32clipboard.SetClipboardData(win32clipboard.RegisterClipboardFormat("HTML Format"), bytearray(html, 'utf-8'))

        win32clipboard.CloseClipboard()

        time.sleep(.1)

        __ctrl_v()

        time.sleep(.1)
        win32clipboard.OpenClipboard(0)
        win32clipboard.EmptyClipboard()
        win32clipboard.CloseClipboard()

def __ctrl_v():
    keyboard.press(Key.ctrl)

    if os.name == 'nt':
        import layout

        l = layout.get_keyboard_language()

        # En keyboard layout
        if l == 'English':
            keyboard.press('v')
            keyboard.release('v')

        # Ru keyboard layout
        if l == 'Russian':
            keyboard.press('м')
            keyboard.release('м')
    else:
        keyboard.press('v')
        keyboard.release('v')

    keyboard.release(Key.ctrl)


def __ctrl_c():
    keyboard.press(Key.ctrl)

    if os.name == 'nt':
        import layout

        l = layout.get_keyboard_language()

        # En keyboard layout
        if l == 'English':
            keyboard.press('c')
            keyboard.release('c')

        # Ru keyboard layout
        if l == 'Russian':
            keyboard.press('с')
            keyboard.release('с')
    else:
        # En keyboard layout
        keyboard.press('c')
        keyboard.release('c')

    # todo Fixe Wordpad bug insert symbol on Past

    keyboard.release(Key.ctrl)
