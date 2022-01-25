from scriptApp.utils import extract_substring
from scriptApp.db import engine, session, Transfer
from PyPDF2 import PdfFileReader
from PyEzFile import File
from os.path import join
from pandas import read_excel, DataFrame
from colorama import Fore
from time import sleep


def load_data(data_path):

    print(f"{Fore.CYAN}Cargando datos...{Fore.RESET}\n")

    sleep(1)

    transfer_file = File(join(data_path, 'Detalle_de_Transferencias.pdf'))

    with open(transfer_file.path, 'rb') as stream:
        inputpdf = PdfFileReader(stream)
        for i in range(inputpdf.numPages):
            page = inputpdf.getPage(i)
            page_content = page.extractText()
            transfer_number = extract_substring(page_content, 'Nro Tef:', 'Nro de Red:')
            try:
                pay_order_number = int(extract_substring(page_content, 'Nro de Orden de Pago:', 'Nro de NC:.'))
            except (TypeError, ValueError):
                pay_order_number = None
            transfer_state = extract_substring(page_content, 'Estados:', 'Observación de la transfer')
            transfer_date = extract_substring(page_content, 'Fecha de Creación:', 'Tipo de transferen')
            try:
                transfer_amount = float((extract_substring(page_content, 'Importe', 'Estados:').replace('.', '').replace(',', '.')))
            except AttributeError:
                transfer_amount = float((extract_substring(page_content, 'Import', 'Estados:').replace('.', '').replace(',', '.')))
            if transfer_state != 'Ejecutada' or pay_order_number is None:
                continue
            record = Transfer(number=transfer_number, pay_order_number=pay_order_number, amount=transfer_amount, state=transfer_state, date=transfer_date)
            session.add(record)
        session.commit()

    print(f"{Fore.YELLOW}Detalle_de_Transferencias.pdf{Fore.RESET} --> {Fore.GREEN}OK{Fore.RESET}")

    sleep(1)

    payment_details_file = File(join(data_path, 'Detalle_de_Pagos.xlsx'))
    data = read_excel(payment_details_file.path)

    provider_df = DataFrame(data, columns=['CODIGO BENEFICIARIO', 'EMAIL - PRESTADOR', 'EMAIL - RESPONSABLE'])
    provider_df.rename(columns={'CODIGO BENEFICIARIO': 'code', 'EMAIL - PRESTADOR': 'email', 'EMAIL - RESPONSABLE': 'cc'}, inplace=True)
    provider_df.drop_duplicates(inplace=True)
    provider_df.to_sql('provider', con=engine, if_exists="append", index=False)

    pay_order_df = DataFrame(data, columns=['OP', 'FC', 'CODIGO BENEFICIARIO'])
    pay_order_df.rename(columns={'OP': 'number', 'FC': 'invoice', 'CODIGO BENEFICIARIO': 'provider_code'}, inplace=True)
    pay_order_df.to_sql('pay_order', con=engine, if_exists="append", index=False)

    print(f"{Fore.YELLOW}Detalle_de_Pagos.xlsx{Fore.RESET} --> {Fore.GREEN}OK{Fore.RESET}")

    sleep(1)
