from scriptApp.db import session, Provider, Transfer, PayOrder
from scriptApp.generator import message, subject, attachments
from scriptApp.utils import log
from PyEzEmail import Email, MailData
from pandas import read_sql_query
from time import sleep


def send_data(datadir, smtpcfg):

    log(f"\nIniciando envio de informes...\n")

    providers = session.query(Provider).all()

    sleep(1)

    i = 0

    for provider in providers:

        sql_query = session.query(PayOrder, Transfer).join(PayOrder, Transfer.pay_order).filter(PayOrder.provider_code == provider.code)
        transfers_dates_df = read_sql_query(sql_query.statement, session.bind).drop_duplicates(subset='date').filter(items=['date']).reset_index(drop=True)

        for index, row in transfers_dates_df.iterrows():

            date = row['date']

            data = MailData(
                to=provider.email.split(';'),
                cc=provider.cc.split(';'),
                bcc=["control.informes.pagos@ossacra.org.ar"],
                subject=subject(date, provider.cuit, provider.name),
                message=message(date),
                attachments=attachments(datadir, date, provider))

            log(f"Enviando: Prestador: {provider.name} - {provider.code} - Mails: {provider.email} - {provider.cc}")

            try:
                Email(smtpcfg, data).send()
            except UnicodeEncodeError:
                data.to = ["UnicodeEncodeError"]
                Email(smtpcfg, data).send()

            i += 1

            sleep(1)
            
            if i == 400:
                log("\n400 mails enviados, entrando en periodo de espera de 1 hora . . .\n")
                sleep(3600)
                i = 0

    sleep(1)

    log(f"\nEnvio finalizado")

    sleep(1)
