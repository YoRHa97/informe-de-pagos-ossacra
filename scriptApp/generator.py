from scriptApp.db import Provider, session, PayOrder, Transfer
from pandas import read_sql_query
from os import listdir
from os.path import join


def detail(datadir: str, date: str, provider: Provider) -> str:
    file_path = join(datadir, f'Detalle_de_Pagos_{date.replace("/", "-")}_{provider.code}.xlsx')
    transfers_df = read_sql_query(session.query(Transfer, PayOrder).join(PayOrder, Transfer.pay_order).filter(PayOrder.provider_code == provider.code).statement, session.bind)
    transfers_df.drop(['id', 'state', 'id_1', 'number_1', 'provider_code'], axis=1, inplace=True)
    transfers_df = transfers_df.loc[transfers_df['date'] == date]
    transfers_df.rename(columns={'number': 'Numero de transferencia', 'amount': 'Monto', 'date': 'Fecha', 'pay_order_number': 'Orden de pago', 'invoice': 'Factura'}, inplace=True)
    transfers_df.to_excel(file_path, index=False)
    return file_path


def attachments(datadir: str, date: str, provider: Provider) -> [str]:
    #attachments_path_list = [detail(datadir, date, provider)]
    attachments_path_list = []
    for file in listdir(join(datadir,'ordenes')):
        payment_orders = provider.payment_orders
        for pay_order in payment_orders:
            if (str(pay_order.transfer.date) == date) and (str(pay_order.number) in file):
                attachments_path_list.append(join(datadir,'ordenes', file))
    for file in listdir(join(datadir,'comprobantes')):
        payment_orders = provider.payment_orders
        for pay_order in payment_orders:
            if (str(pay_order.transfer.date) == date) and (str(pay_order.transfer.number) in file):
                attachments_path_list.append(join(datadir,'comprobantes', file))
    return attachments_path_list


def subject(date: str, cuit: str, name: str) -> str:
    return (
        f'Informe de pagos - {cuit} - {name} - Transferencias {date} - OSSACRA'
    )


def message(date: str) -> str:
    return (
        f'''
            <h2>Estimado/a:</h2>
            <h3>Se adjuntan las ordenes de pago, comprobantes de transferencias y detalle de los pagos realizados el dia {date} .</h3>
            <p>
                <table align="center" width="75%">
                    <tr>
                        <th>
                            <div style="margin: 0 auto; text-align: center;">
                                <p>
                                    <img src="https://ossacra.org.ar/wp-content/uploads/2020/08/cropped-logo_amasalud_horizontal-650.png" alt="" 
                                    style="display: block; margin-left: auto; margin-right: auto;" width="489" height="109" />
                                </p>
                            </div>
                        </th>
                    </tr>
                </table>
            </p>
        '''
    )
