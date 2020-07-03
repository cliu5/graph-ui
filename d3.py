from influxdb import InfluxDBClient, DataFrameClient
import pandas as pd
import datetime
import time
import os
import math
import csv

HOST_1 = 'ec2-35-183-41-80.ca-central-1.compute.amazonaws.com'
HOST_2 = 'ec2-35-182-170-72.ca-central-1.compute.amazonaws.com'

database = 'md_rates'
user_name = 'xren'
passwords = '5X%UZ^Xa.bH@9Ze6'
client = InfluxDBClient(host=HOST_2, port=8086, username=user_name, password=passwords)
client.switch_database(database)

'''notes on coin accuracy
- BTC price for binance and okex about $200 off, but corrected itself after a few refreshes
- bybit is usually exact
- my bitmex eth exchange is 80m and skew says 110 (but i added from bitmex website)
- altcoin oi doesn't include perp swap (ex: xrp), keep in mind when looking at aggregate oi
'''

exchanges = ['huobi_dm_open_interest', 'okex_ticker', 'bitmex_instrument', 'okex_SwapOpenInterest','binance_open_interest_clean']
#exchanges = ['huobi_dm_open_interest', 'okex_ticker', 'bitmex_instrument', 'okex_SwapOpenInterest']

prices = dict()
open_interest = dict()
all_price_tokens=['BTC', 'ETH','BCH','LTC','XRP','BSV','TRX','EOS','ADA','ETC','LINK','XLM']
hour = '2h'
bitcon_price = 0

bitmex_tokens=['XBT','ETH','EOS','BCH','XRP','TRX','ADA','LTC']
huobi_tokens=['BTC', 'ETH', 'BCH', 'XRP', 'BSV', 'TRX', 'EOS', 'ETC']
okex_tokens=['BTC', 'ETH','BCH','LTC','XRP','BSV','TRX','EOS','ETC']
binance_tokens=['BTC', 'ETH','BCH','EOS','XRP','LTC','TRX','LINK','XLM']
bybit_tokens=['BTC', 'ETH', 'EOS', 'XRP']
deribit_tokens=['BTC','ETH']

def make_dates():
    today = datetime.date.today()

    weekly = today + datetime.timedelta( (3-today.weekday()) % 7 + 1 )
    biweekly = weekly + datetime.timedelta(7)
    weekly_str = weekly.strftime('%y%m%d')
    biweekly_str = biweekly.strftime('%y%m%d')

    quarterly = datetime.date(2020, 3, 27)
    quarterly_str = quarterly.strftime('%y%m%d')

    june = datetime.date(2020, 6, 26)
    june_str = june.strftime('%y%m%d')

    dates = [weekly_str,biweekly_str,quarterly_str,june_str]

    #for deribit

    biweekly = datetime.datetime.strptime(dates[2], '%y%m%d')
    biweekly_str = biweekly.strftime('%d%b%y')
    biweekly_str = biweekly_str[:2] + biweekly_str[2:5].upper() + biweekly_str[5:]

    quarterly = datetime.datetime.strptime(dates[3], '%y%m%d')
    quarterly_str = quarterly.strftime('%d%b%y')
    quarterly_str = quarterly_str[:2] + quarterly_str[2:5].upper() + quarterly_str[5:]

    deribit_contracts = ['PERPETUAL'] + [biweekly_str,quarterly_str]
    dates += [biweekly_str,quarterly_str]

    return dates

dates = make_dates()

for token in all_price_tokens:
    prices[token] = dict()

def strip_time(x):
    try:
        len_of_decimal = len(x.split('.')[1])
        if len_of_decimal > 6:
            len_of_decimal -= 6
            x = x[:-len_of_decimal]
        else:
            x = x[:-1]
        return time.mktime(datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f").timetuple())
    except:
        x = x[:-1]
        return time.mktime(datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S").timetuple())


def find_liquidation():
    tokens = ['XBTUSD', 'XBTH20', 'XBTM20', 'ETHUSD', 'ETHH20', 'BCHH20', 'LTCH20', 'ADAH20', 'TRXH20', 'XRPH20', 'EOSH20']
    liquidations = {}
    for token in tokens:
        liquidation_query = f"select * from bitmex_liquidation where time >= now() - 5d and symbol =~ /{token}/"
        df = pd.DataFrame(client.query(liquidation_query, chunked=True, chunk_size=10000).get_points())
        data = df.to_dict()
        token_liquidations = {'Buy':{},'Sell':{}}
        for key in data['time']:
            t = time.mktime(datetime.datetime.strptime(data['time'][key][:-4], "%Y-%m-%dT%H:%M:%S.%f").timetuple())
            token_liquidations[data['side'][key]][int(t)] = data['leavesQty'][key]
        liquidations[token] = token_liquidations
    for token in liquidations.keys():
        path = "static/js/"
        with open(path + token + '-liquidations.csv', 'w') as f:
            f.write("Hrs,Liq," + "BuySell" + '\n')
            for buyOrSell in liquidations[token].keys():
                for hrsAgo in liquidations[token][buyOrSell].keys():
                    f.write(str(hrsAgo // 10000) + "," + str(liquidations[token][buyOrSell][hrsAgo]) + "," + buyOrSell + "\n")
            ''' 
            with open(token + '-liquidations-' + buyOrSell + '.csv', 'w') as f:
                f.write("Hrs Ago, Total Hourly Liquidations \n")
                for hrsAgo in liquidations[token][buyOrSell].keys():
                    f.write(str(hrsAgo // 10000) + "," + str(liquidations[token][buyOrSell][hrsAgo]) + "\n")
                #f.write(liquidations[token][buyOrSell])
                #f.write("%s,%s\n"%(liquidations[token][buyOrSell], '\n'))
            '''
    #f.close()
    return liquidations

if __name__ == "__main__":
    find_liquidation()

# #structure of open_interest
# by exchange, by coin, by contract, time: {symbol, open_interest} -careful some OI are diff formated
#
# #structure of price
# by coin, by exchange, time: {symbol, price} - careful some is "last"
