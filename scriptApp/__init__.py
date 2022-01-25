from scriptApp.db import Provider, PayOrder, Transfer
from scriptApp.loader import load_data
from scriptApp.sender import send_data
from scriptApp.utils import askdirectory
from colorama import Fore
from getpass import getpass
from PyEzEmail import SmtpConfig
from time import sleep
from os import system


def mainscript():
    host = input(f"Host: {Fore.GREEN}")
    username = input(f"{Fore.RESET}Username: {Fore.GREEN}")
    password = getpass(f'{Fore.RESET}Password: ')

    system("cls" or "clear")

    print(f"Conectando...")

    smtpcfg = SmtpConfig(
        username=username,
        password=password,
        host=host,
        port=25
    )

    system("cls" or "clear")

    print(f"{Fore.GREEN}Conexion establecida correctamente!{Fore.RESET}\n")

    sleep(1)

    print(f"{Fore.CYAN}Seleccione la carpeta con los datos a procesar:{Fore.RESET}\n")

    sleep(1)

    datadir = askdirectory()

    load_data(datadir)
    send_data(datadir, smtpcfg)
