from scriptApp.db import session, Provider, Transfer, PayOrder
from scriptApp.generator import message, subject, attachments
from PyEzEmail import Email, MailData
from pandas import read_sql_query
from colorama import Fore
from time import sleep


def send_data(datadir, smtpcfg):

    print(f"\n{Fore.CYAN}Iniciando envio de informes...{Fore.RESET}\n")

    providers = session.query(Provider).all()

    sleep(1)

    for provider in providers:
        sql_query = session.query(PayOrder, Transfer).join(PayOrder, Transfer.pay_order).filter(PayOrder.provider_code == provider.code)
        transfers_dates_df = read_sql_query(sql_query.statement, session.bind).drop_duplicates(subset='date').filter(items=['date']).reset_index(drop=True)
        for index, row in transfers_dates_df.iterrows():
            date = row['date']
            data = MailData(
                to=[provider.email],
                cc=[provider.cc],
                bcc=[smtpcfg.username],
                subject=subject(date),
                message=message(date, provider.cc),
                attachments=attachments(datadir, date, provider))
            print(f"{Fore.CYAN}Enviando:{Fore.RESET} Codigo: {Fore.LIGHTMAGENTA_EX}{provider.code}{Fore.RESET} - Mail: {Fore.LIGHTMAGENTA_EX}{provider.email}{Fore.RESET}")
            Email(smtpcfg, data).send()
            sleep(1)

    sleep(1)

    print(f"\n{Fore.GREEN}Envio finalizado.{Fore.RESET}")

    sleep(1)
