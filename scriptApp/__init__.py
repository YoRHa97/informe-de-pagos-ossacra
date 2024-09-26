from scriptApp.loader import load_data
from scriptApp.sender import send_data
from scriptApp.utils import askdirectory, log
from colorama import Fore
from getpass import getpass
from time import sleep
from os import system


def mainscript():
    system("cls" or "clear")
    log(f"{Fore.CYAN}Seleccione la carpeta con los datos a procesar:{Fore.RESET}\n")
    sleep(1)
    datadir = askdirectory()
    load_data(datadir)
    send_data(datadir)
