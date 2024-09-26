import time
from scriptApp.utils import log, extract_substring
from scriptApp.db import engine, session, Transfer
from PyPDF2 import PdfFileReader
from os.path import join
from pandas import read_excel, DataFrame
from colorama import Fore


def load_data(dir_path):
    log(f"{Fore.CYAN}Cargando datos...{Fore.RESET}\n")
    time.sleep(1)
    with open(join(dir_path, 'Detalle_de_Transferencias.pdf'), 'rb') as stream:
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
            if transfer_state not in ['Ejecutada', 'Enviada banco credito'] or pay_order_number is None:
                continue
            record = Transfer(number=transfer_number, pay_order_number=pay_order_number, amount=transfer_amount, state=transfer_state, date=transfer_date)
            session.add(record)
        session.commit()
    log(f"{Fore.YELLOW}Detalle_de_Transferencias.pdf{Fore.RESET} --> {Fore.GREEN}OK{Fore.RESET}")
    time.sleep(1)
    data = read_excel(join(dir_path, 'Detalle_de_Pagos.xlsx'))
    provider_df = DataFrame(data, columns=['CODIGO BENEFICIARIO', "BENEFICIARIO", 'CUIT', 'EMAIL-PRESTADOR', 'EMAIL-RESPONSABLE'])
    provider_df.rename(columns={'CODIGO BENEFICIARIO': 'code', 'BENEFICIARIO': 'name', 'CUIT': 'cuit', 'EMAIL-PRESTADOR': 'email', 'EMAIL-RESPONSABLE': 'cc'}, inplace=True)
    provider_df.drop_duplicates(inplace=True)
    provider_df.to_sql('provider', con=engine, if_exists="append", index=False)
    pay_order_df = DataFrame(data, columns=['OP', 'FC', 'CODIGO BENEFICIARIO'])
    pay_order_df.rename(columns={'OP': 'number', 'FC': 'invoice', 'CODIGO BENEFICIARIO': 'provider_code'}, inplace=True)
    pay_order_df.to_sql('pay_order', con=engine, if_exists="append", index=False)
    log(f"{Fore.YELLOW}Detalle_de_Pagos.xlsx{Fore.RESET} --> {Fore.GREEN}OK{Fore.RESET}")
    time.sleep(1)
