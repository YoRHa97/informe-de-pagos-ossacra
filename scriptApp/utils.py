from tkinter import Tk, filedialog
from re import search


def extract_substring(string, substring_left, substring_right):
    result = search(f'{substring_left}(.*?){substring_right}', string)
    try:
        match = result.group(1)
        return match
    except AttributeError:
        return None


def askdirectory():
    root = Tk()
    root.withdraw()
    return filedialog.askdirectory()
