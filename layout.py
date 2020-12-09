from win32gui import GetForegroundWindow
from win32process import GetWindowThreadProcessId
from win32api import GetKeyboardLayout


def get_keyboard_language():
    languages = {'0x409': 'English', '0x419': 'Russian'}

    # Get the current active window handle
    handle = GetForegroundWindow()

    # Get the thread id from that window handle
    threadid, processid = GetWindowThreadProcessId(handle)

    # Get the keyboard layout id from the threadid
    layout_id = GetKeyboardLayout(threadid)

    # Extract the keyboard language id from the keyboard layout id
    language_id = layout_id & (2 ** 16 - 1)

    # Convert the keyboard language id from decimal to hexadecimal
    language_id_hex = hex(language_id)

    # Check if the hex value is in the dictionary.
    if language_id_hex in languages.keys():
        return languages[language_id_hex]
    else:
        # Return language id hexadecimal value if not found.
        return str(language_id_hex)