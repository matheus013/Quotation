import datetime
import json
import time

import pandas as pd
import requests
from pycoingecko import CoinGeckoAPI

wallet = '0x35cac134b8a88edddd3d0b1d5c2157415748b159'  # m

cg = CoinGeckoAPI()

xls = pd.ExcelFile('data/10.01.2021-11.16.2021.xltx')  # Setting file from bscscan
df = pd.read_excel(xls, 'Tansactions')
df_tokens = pd.read_excel(xls, 'BEP-20 Token Transfer Events')

request = requests.get('https://economia.awesomeapi.com.br/all/USD-BRL')
quotation = request.json()

bnb_usd_by_date = json.load(open("data/bnb_usd_by_date.json"))

name_coin_id = {
    'BCOIN': 'bomber-coin',
    'KWT': 'kawaii-islands',
    'PVU': 'plant-vs-undead-token',
    'DSBOWL': 'doge-superbowl',
    'FPVU': 'bomber-coin',
}


def quotation_by_date(dt_ref, target='binancecoin', ref='usd'):
    if target not in bnb_usd_by_date:
        bnb_usd_by_date[target] = {}
    if dt_ref in bnb_usd_by_date[target]:
        return bnb_usd_by_date[target][dt_ref]
    print(dt_ref, target, ref)
    check_date = cg.get_coin_history_by_id(id=target, date=dt_ref)
    current_price = check_date['market_data']['current_price'][ref]
    print(f'DATE: {dt_ref}; {target}/{ref}:', "$ {:,.2f}".format(current_price))
    bnb_usd_by_date[target][dt_ref] = current_price
    time.sleep(10)
    return current_price


print('#### Cotação do Dolar Hoje ####')
print('Moeda:', quotation['USD']['name'])
print('Data:', quotation['USD']['create_date'])
print('Valor atual: R$:', quotation['USD']['bid'], '\n\n')

BRL_USD = quotation['USD']['bid']

df['DateTime'] = df['DateTime'].dt.strftime('%d-%m-%Y')
df_tokens['DateTime'] = df_tokens['DateTime'].dt.strftime('%d-%m-%Y')
df['total'] = df['Value_IN(BNB)'] - df['Value_OUT(BNB)']
in_total = 0.0
out_total = 0.0

token_in = {}
token_out = {}

for index, row in df.iterrows():
    dt = row['DateTime']

    # print(row['Txhash'], row['Txhash'] in df_tokens.Txhash)
    bep_20 = df_tokens[df_tokens['Txhash'] == row['Txhash']]
    if not bep_20.empty and row['total'] == 0:
        aux = bep_20[['To', 'Value', 'TokenSymbol']].values.tolist()[0]
        if aux[2] in name_coin_id:
            token_quote = quotation_by_date(dt, target=name_coin_id[aux[2]])
            if not aux[2] in token_in:
                token_in[aux[2]] = 0
                token_out[aux[2]] = 0
            if aux[0] == wallet:
                token_in[aux[2]] += aux[1] * token_quote
            if aux[0] == wallet:
                token_in[aux[2]] += aux[1] * token_quote

    quote = quotation_by_date(dt)

    value_total = row['total'] * quote

    if value_total > 0.0:
        in_total += float(value_total)
    else:
        out_total += float(value_total)

for index, row in df_tokens.iterrows():
    dt = row['DateTime']
    bep_20 = df[df['Txhash'] == row['Txhash']]
    if bep_20.empty:
        aux = [row['To'], row['Value'], row['TokenSymbol']]
        if aux[2] in name_coin_id:
            token_quote = quotation_by_date(dt, target=name_coin_id[aux[2]])
            if not aux[2] in token_in:
                token_in[aux[2]] = 0
                token_out[aux[2]] = 0
            if aux[0] == wallet:
                token_in[aux[2]] += aux[1] * token_quote
            else:
                token_out[aux[2]] += aux[1] * token_quote
sum_in_total = in_total
sum_out_total = out_total

print(f"Total BNB (in):", "$ {:,.2f}".format(in_total), "R$ {:,.2f}".format(float(in_total) * float(BRL_USD)))
print(f"Total BNB (out):", "$ {:,.2f}".format(out_total), "R$ {:,.2f}".format(float(out_total) * float(BRL_USD)))

for key, value in token_in.items():
    print(f"Total {key} (in):", "$ {:,.2f}".format(value), "R$ {:,.2f}".format(float(value) * float(BRL_USD)))
    print(f"Total {key} (out):", "$ {:,.2f}".format(token_out[key]),
          "R$ {:,.2f}".format(float(token_out[key]) * float(BRL_USD)))
    sum_out_total += token_out[key]
    sum_in_total += value

print(f"\nTotal (in):", "$ {:,.2f}".format(sum_in_total), "R$ {:,.2f}".format(float(sum_in_total) * float(BRL_USD)))
print(f"Total (out):", "$ {:,.2f}".format(sum_out_total),
      "R$ {:,.2f}".format(float(sum_out_total) * float(BRL_USD)))

json.dump(bnb_usd_by_date, open("data/bnb_usd_by_date.json", 'w'))
