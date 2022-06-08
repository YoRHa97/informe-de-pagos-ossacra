from tkinter import Tk, filedialog
from re import search


def log(string: str):
    print(string)
    with open("log.txt", "a") as log_file:
        log_file.write(string+"\n")


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
