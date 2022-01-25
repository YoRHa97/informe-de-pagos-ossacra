from os import system
from colorama import Fore
from signal import signal, SIGINT
from traceback import print_exc
from scriptApp import mainscript


def exit_handler(signum, frame):
    print(f'\n{Fore.RESET}')
    system("cls" or "clear")
    exit(1)


if __name__ == '__main__':
    system("cls" or "clear")
    signal(SIGINT, exit_handler)
    try:
        mainscript()
    except Exception as Ex:
        print(f'\n{Fore.LIGHTRED_EX}{Ex}{Fore.RESET}')
        with open('exception.txt', 'w+') as f:
            print_exc(file=f)
    input("\nPresione una tecla para finalizar . . .")
