from datetime import datetime
import pandas as pd
import json
import requests
# from web3 import Web3
import requests

API_KEY = 'Z3X5HF59YG8M3H58YIGIZWN3ZRBCI6R3K5'
ADDRESS = '0x35CAc134b8A88EdDdD3D0b1D5C2157415748b159'
TokenAddress = "0x00e1656e45f18ec6747f5a8496fd39b50b38396d"
bsc = "https://bsc-dataseed.binance.org/"
# web3 = Web3(Web3.HTTPProvider(bsc))
url_eth = "https://api.bscscan.com/api"
# contract_address = web3.toChecksumAddress(TokenAddress)
API_ENDPOINT = url_eth + "?module=contract&action=getabi&address=" + '0x00e1656e45f18ec6747f5a8496fd39b50b38396d'
r = requests.get(url=API_ENDPOINT)
response = r.json()
abi = json.loads(response["result"])

print(abi)