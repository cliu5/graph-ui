from influxdb import InfluxDBClient, DataFrameClient
import pandas as pd
import os
import math
import csv


HOST_1 = 'ec2-15-222-236-45.ca-central-1.compute.amazonaws.com'
HOST_2 = 'ec2-15-223-67-67.ca-central-1.compute.amazonaws.com'


database = 'md_rates'
user_name = 'xren'
passwords = '5X%UZ^Xa.bH@9Ze6'
client = InfluxDBClient(host=HOST_2, port=8086, username=user_name, password=passwords)
client.switch_database(database)

exchanges = ['huobi_dm_open_interest', 'okex_ticker', 'bitmex_instrument', 'okex_SwapOpenInterest','binance_open_interest_clean']
#exchanges = ['huobi_dm_open_interest', 'okex_ticker', 'bitmex_instrument', 'okex_SwapOpenInterest']

weekly = "200619"
biweekly = "200626"
quarterly = "200626"
biquarterly = "200925"
deribit_quarterly = "26JUN20"
deribit_biquarterly = "25SEP20"
deribit_semi = "25DEC20"
ftx_quarterly = "0626"
ftx_biquarterly = "0925"

def find_price():
    prices = {}
    bitmex_price = {}
    huobi_price = {}
    bitmex_tokens=['XBTUSD','ETHUSD', 'BCHM20','XRPUSD','TRXM20','ADAM20','EOSM20']
    for token in bitmex_tokens:
        #bitmex_query = f"select * from bitmex_trade where time >= now() - 12h"
        bitmex_query = f"select last(price),symbol from bitmex_trade where time >= now() - 24h and symbol =~ /{token}/"
        df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
        data = df.to_dict()
        if (token == 'XBTUSD'):
            bitmex_price['BTCUSD'] = round(data['last'][0],3)
        else:
            bitmex_price[token] = data['last'][0]
    prices['bitmex'] = bitmex_price

    huobi_tokens=['BTC', 'ETH', 'BCH', 'XRP', 'BSV', 'TRX', 'EOS', 'ETC']
    for token in huobi_tokens:
        # perp data
        huobi_query = f"select last(index_price),symbol from huobidm_index_price where time >= now() - 30m and symbol =~ /{token}/"
        df = pd.DataFrame(client.query(huobi_query, chunked=True, chunk_size=10000).get_points())
        data = df.to_dict()
        huobi_price[token + 'USD'] = round(data['last'][0],3)
        # futures data
        '''
        huobi_query = f"select last(price),symbol from huobidm_trades where time >= now() - 30m and symbol =~ /{token}/"
        df = pd.DataFrame(client.query(huobi_query, chunked=True, chunk_size=10000).get_points())
        data = df.to_dict()
        print(df)
        '''
    prices['huobi']=huobi_price

    okex_price={}
    okex_tokens=['BTC', 'ETH','BCH','LTC','XRP','BSV','TRX','EOS','ETC']
    for token in okex_tokens:
        okex_query = f"select last(price),symbol from okex_recentTrades where time >= now() - {'24h'} and symbol =~ /{token + '-USD-SWAP'}/"
        df = pd.DataFrame(client.query(okex_query, chunked = True, chunk_size = 10000).get_points())
        data = df.to_dict()
        num = float(data['last'][0])
        okex_price[token + 'USD'] = round(num,4)

    prices['okex']=okex_price

    binance_tokens= ['TRXUSDT',  'ADAUSDT', 'LTCUSDT',
    'ETHUSDT' ,'EOSUSDT' , 'ETCUSDT' ,'XLMUSDT', 'BCHUSDT' ,
    'LINKUSDT' , 'XRPUSDT' , 'BTCUSDT']
    binance_price = {}
    for token in binance_tokens:
        binance_query = f"select last(price),symbol from binance_orderbook_futures_clean where time >= now() - 30m and symbol =~ /{token}/"
        df = pd.DataFrame(client.query(binance_query, chunked=True, chunk_size=10000).get_points())
        data = df.to_dict()
        binance_price[token[0: len(token) - 1]] = round(data['last'][0],3)

    prices['binance']=binance_price

    bybit_price={}
    bybit_tokens=['BTC', 'ETH', 'EOS', 'XRP']
    for token in bybit_tokens:
        bybit_query = f"select last(last_price),symbol from bybit_tickers where time >= now() - 30m and symbol =~ /{token}/"
        df = pd.DataFrame(client.query(bybit_query, chunked=True, chunk_size=10000).get_points())
        data = df.to_dict()
        num = float(data['last'][0])
        bybit_price[token + 'USD'] = round(num,3)

    prices['bybit']=bybit_price

    deribit_price = {}
    deribit_tokens = ['BTC','ETH']
    for token in deribit_tokens:
        deribit_query = f"select last(index_price),symbol from deribit_trades where time >= now() - 24h and symbol =~ /{token + '-PERPETUAL'}/"
        df = pd.DataFrame(client.query(deribit_query, chunked=True, chunk_size=10000).get_points())
        data = df.to_dict()
        deribit_price[token + 'USD'] = round(data['last'][0],3)
    prices['deribit']=deribit_price

    ftx_price= {}
    ftx_tokens = ['BTC-PERP', 'BSV-PERP', 'BCH', 'BNB', 'ADA', 'ATOM']
    for token in ftx_tokens:
        #ftx_query = f"select * from FTX_future_stats where time >= now() - 1h"
        ftx_query = f"select last(price),symbol from FTX_trades where time >= now() - 24h and symbol =~ /{token}/"
        df = pd.DataFrame(client.query(ftx_query, chunked=True, chunk_size=10000).get_points())
        #print(df)
        data = df.to_dict()
        if token == 'BTC-PERP':
            ftx_price['BTCUSD'] = data['last'][0]
        elif token == 'BSV-PERP':
            ftx_price['BSVUSD'] = data['last'][0]
        else:
            ftx_price[token + 'USD'] = data['last'][0]
    prices['ftx'] = ftx_price

    prev = 0
    percent = 0
    tokens = ['BTC','ETH','LTC','XRP','BSV','TRX','EOS','ADA','ETC','LINK', 'XLM']
    exchanges = ['bitmex','huobi','okex','binance','deribit','bybit', 'ftx']
    for token in tokens:
        path = "static/js/prices/"
        with open (path + token + '-prices.csv', 'w') as f:
            f.write('exchange,price,percent' + '\n')
            for exchange in exchanges:
                if token + 'USD' in prices[exchange]:
                    if exchange == 'bitmex':
                        f.write(exchange + ',' + str(prices[exchange][token+'USD']) + ',0.000%' + "\n")
                        prev = prices[exchange][token+'USD']
                    else:
                        percent = round(((prices[exchange][token+'USD'] - prev) / -100), 3)
                        f.write(exchange + ',' + str(prices[exchange][token+'USD']) + ','
                        + str(percent) + "% \n")

def make_table():
    table = {}
    bitmex_price={}
    exchanges = ['bitmex','huobi','okex','binance','deribit','bybit', 'ftx']
    futures = ['PERP', weekly, biweekly, quarterly, biquarterly]
    bitmex_tokens = ['XBTM20', 'XBTU20', 'ETHM20']
    for token in bitmex_tokens:
        bitmex_query = f"select last(price),symbol from bitmex_trade where time >= now() - 12h and symbol =~ /{token}/"
        df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
        data = df.to_dict()
        if (token == 'XBTM20'):
            bitmex_price['BTC' + quarterly] = round(data['last'][0],3)
        elif (token == 'XBTU20'):
            bitmex_price['BTC' + biquarterly] = data['last'][0]
        elif (token == 'ETHM20'):
            bitmex_price['ETH' + quarterly] = data['last'][0]

    table['bitmex'] = bitmex_price

    huobi_price={}
    huobi_tokens=['BTC' + weekly, 'BTC' + biweekly, 'BTC' + quarterly, 'ETH' + weekly, 'ETH' + biweekly, 'ETH' + quarterly]
    for token in huobi_tokens:
        huobi_query = f"select last(price),symbol from huobidm_trades where time >= now() - 12h and symbol =~ /{token}/"
        df = pd.DataFrame(client.query(huobi_query, chunked=True, chunk_size=10000).get_points())
        data = df.to_dict()
        huobi_price[token] = data['last'][0]
    table['huobi'] = huobi_price

    okex_price={}
    okex_tokens=['BTC-USD-' + weekly,'BTC-USD-' + quarterly , 'BTC-USD-' + biquarterly,'BTC-USD-' + biweekly,
                'ETH-USD-' + weekly, 'ETH-USD-' + quarterly, 'ETH-USD-' + biquarterly, 'ETH-USD-' + biweekly]
    for token in okex_tokens:
        okex_query = f"select last(price),symbol from okex_recentTrades where time >= now() - 24h and symbol =~ /{token}/"
        df = pd.DataFrame(client.query(okex_query, chunked = True, chunk_size = 10000).get_points())
        data = df.to_dict()
        if token == 'BTC-USD-' + weekly:
            num = float(data['last'][0])
            okex_price['BTC' + weekly] = round(num,3)
        elif token == 'BTC-USD-' + biweekly:
            num = float(data['last'][0])
            okex_price['BTC' + biweekly] = round(num,3)
        elif token == 'BTC-USD-' + quarterly:
            num = float(data['last'][0])
            okex_price['BTC' + quarterly] = round(num,3)
        else: 
            num = float(data['last'][0])
            okex_price[token[0:3] + token[-6:]] = round(num,3)
    table['okex'] = okex_price

    deribit_price = {}
    deribit_tokens = ['BTC-' + deribit_quarterly,'BTC-' + deribit_biquarterly, 'ETH-' + deribit_quarterly,'ETH-' + deribit_biquarterly]
    for token in deribit_tokens:
        deribit_query = f"select last(price),symbol from deribit_trades where time >= now() - 12h and symbol =~ /{token}/"
        df = pd.DataFrame(client.query(deribit_query, chunked=True, chunk_size=10000).get_points())
        data = df.to_dict()
        if token == 'BTC-' + deribit_quarterly:
            deribit_price['BTC' + quarterly] = round(data['last'][0],3)
        elif token == 'BTC-' + deribit_biquarterly:
            deribit_price['BTC' + biquarterly] = round(data['last'][0],3)
        elif token == 'ETH-' + deribit_quarterly:
            deribit_price['ETH' + deribit_quarterly] = round(data['last'][0],3)
        elif token == 'ETH-' + deribit_biquarterly:
            deribit_price['ETH' + deribit_biquarterly] = round(data['last'][0],3)
        
    table['deribit'] = deribit_price

    ftx_price= {}
    ftx_tokens = ['BTC-' + ftx_quarterly ,'BTC-' + ftx_biquarterly, 'ETH-' + ftx_quarterly]
    for token in ftx_tokens:
        #ftx_query = f"select last(price),symbol from FTX_future_stats where time >= now() - 1h and symbol =~/{token}/"
        ftx_query = f"select last(price),symbol from FTX_trades where time >= now() - 12h and symbol =~/{token}/"
        df = pd.DataFrame(client.query(ftx_query, chunked=True, chunk_size=10000).get_points())
        data = df.to_dict()
        if token == 'BTC-' + ftx_quarterly:
            ftx_price['BTC' + quarterly] = data['last'][0]
        elif token == 'BTC-' + ftx_biquarterly:
            ftx_price['BTC' + biquarterly] = data['last'][0]
        elif token == 'ETH-' + ftx_quarterly:
            ftx_price['ETH' + quarterly] = data['last'][0]

    table['ftx'] = ftx_price

    exchanges = ['bitmex','huobi','okex','deribit','ftx']
    futures = ['BTC' + weekly, 'BTC' + biweekly, 'BTC' + quarterly, 'BTC' + biquarterly,
                'ETH' + weekly, 'ETH' + biweekly, 'ETH' + quarterly, 'ETH' + biquarterly]
    for exchange in exchanges:
        for future in futures:
            if future not in table[exchange]:
                table[exchange][future] = '-'
    
    
    path = "static/js/prices/"
    exchanges = ['BTC','ETH']
    futures = [weekly, biweekly, quarterly, biquarterly]
    for exchange in exchanges:
        with open (path  +  exchange + '-table-prices.csv', 'w') as f:
            f.write('expiry,bitmex,huobi,okex,deribit,ftx' + '\n')
            for future in futures: 
                f.write(exchange + future + ',' + str(table['bitmex'][exchange + future]) + ',' + str(table['huobi'][exchange + future]) +
                ',' + str(table['okex'][exchange + future]) + ',' + str(table['deribit'][exchange + future]) + 
                ',' + str(table['ftx'][exchange + future]) + '\n')

comparisons = {'bitmex':0, 'okex':0, 'huobi':0, 'binance':0,'deribit':0,'ftx':0, 'bybit':0}        
def bitmex():
    global bitcoin_price
    s = []
    bitmex_oi = dict()
    exchange = 'bitmex'
    tokens = ['XBTUSD', 'XBTM20', 'XBTU20' , 'ETHUSD', 'BCHM20', 'TRXM20', 'ETHM20', 'LTCM20', 'ADAM20', 'XRPUSD', 'XRPM20', 'EOSM20']
    time = ["1h", "2h", "12h", "1d"]
    #time = ["1h", "2h", "12h", "1d", "3d" ]
    emptyTokens={}
    for time_period in time:
        open_interest={}
        for token in tokens:
            bitmex_query = f"select usd_denominated_open_interest,coin_denominated_open_interest,contract_symbol from exchange_open_interest where time >= now() - {time_period} and contract_exchange =~ /Bitmex/ and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if len(data) == 0:
                emptyTokens[token] = time_period
                continue
            df = df.fillna(method='bfill')
            path = "static/js/open-interest/"
            with open(path + exchange + "-" + time_period + "-" + token + '-open-interest-usd.csv', 'w') as f:
                f.write("date,value" + "\n")
                for key in data['time']:
                    t = data['time'][key][0:19]
                    if(data['usd_denominated_open_interest'][key] == 0 or data['contract_symbol'][key] != token):
                        continue
                    f.write(t + "," + str(data['usd_denominated_open_interest'][key]) + "\n")
            
            with open(path + exchange + "-" + time_period + "-" + token + '-open-interest-coin.csv', 'w') as f:
                f.write("date,value" + "\n")
                for key in data['time']:
                    t = data['time'][key][0:19]
                    if(data['coin_denominated_open_interest'][key] == 0 or data['contract_symbol'][key] != token):
                        continue
                    f.write(t + "," + str(data['coin_denominated_open_interest'][key]) + "\n")

    for key in emptyTokens:
        path = "static/js/open-interest/"
        with open(path + exchange + "-" + str(emptyTokens[key]) + "-" + key + '-open-interest-usd.csv', 'w') as f:
            f.write("date,value" + "\n")
    
    for key in emptyTokens:
        path = "static/js/open-interest/"
        with open(path + exchange + "-" + str(emptyTokens[key]) + "-" + key + '-open-interest-coin.csv', 'w') as f:
            f.write("date,value" + "\n")
            """
    emptyTokens = {}
    for time_period in time:
        for token in tokens: 
            #bitmex_query = f"select * from exchange_open_interest where time>= now() - {time_period}"
            bitmex_query = f"select coin_denominated_open_interest,contract_symbol from exchange_open_interest where time >= now() - {time_period} and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if len(data) == 0:
                emptyTokens[token] = time_period
                continue
            df = df.fillna(method='bfill')
            path = "static/js/open-interest/"
            with open(path + exchange + "-" + time_period + "-" + token + '-open-interest-coin.csv', 'w') as f:
                f.write("date,value" + "\n")
                for key in data['time']:
                    t = data['time'][key][0:19]
                    if(data['coin_denominated_open_interest'][key] == 0 or data['contract_symbol'][key] == token + 'T'):
                        continue
                    f.write(t + "," + str(data['coin_denominated_open_interest'][key]) + "\n")
    for key in emptyTokens:
        path = "static/js/open-interest/"
        with open(path + exchange + "-" + str(emptyTokens[key]) + "-" + key + '-open-interest-coin.csv', 'w') as f:
            f.write("date,value" + "\n")
            """
    

def bitmex_volume():
    exchange = 'bitmex'
    tokens = ['XBTUSD', 'XBTM20', 'XBTU20' , 'ETHUSD', 'BCHM20', 'TRXM20', 'ETHM20', 'LTCM20', 'ADAM20', 'XRPUSD', 'XRPM20', 'EOSM20']
    time = ["1h", "2h", "12h", "1d"]
    emptyTokens={}
    for time_period in time:
        open_interest={}
        for token in tokens:
            #bitmex_query = f"select * from bitmex_instrument where time >= now() - {time_period} and symbol =~ /{token}/ GROUP BY time(10m) fill(previous)"
            bitmex_query = f"select volume24h,symbol from bitmex_instrument where time >= now() - {time_period} and symbol =~ /{token}/"
            df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if len(data) == 0:
                emptyTokens[token] = time_period
                continue
            df = df.fillna(method='bfill')
            path = "static/js/volume/"
            with open(path + exchange + "-" + time_period + "-" + token + '-volume.csv', 'w') as f:
                f.write("date,value" + "\n")
                for key in data['time']:
                    t = data['time'][key][0:19]
                    if(data['volume24h'][key] == 0 or data['symbol'][key] != token):
                        continue
                    f.write(t + "," + str(data['volume24h'][key]) + "\n")            
          
def huobi():
    s = []
    emptyTokens={}
    exchange = 'huobi'
    coins = ['BTC', 'ETH', 'TRX', 'BSV', 'XRP', 'BCH', 'EOS', 'ETC', 'LTC']
    tokens = []
    for coin in coins:
        tokens.append(coin + weekly)
        tokens.append(coin + biweekly)
        tokens.append(coin + quarterly)
        tokens.append(coin + '-USD')

    time = ["1h", "2h", "12h", "1d"]
    #time = ["1h", "2h", "12h", "1d", "3d" ]
    for time_period in time:
        open_interest={}
        for token in tokens:
            bitmex_query = f"select * from huobidm_open_interest where time >= now() - {time_period} and contract_code =~ /{token}/"
            df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
            df = df.rename(columns={'first': 'open_interest'})
            data = df.to_dict()     
            if len(data) == 0:
                emptyTokens[token] = time_period
                continue       
            df = df.fillna(method='bfill')
            path = "static/js/open-interest/"
            with open(path + exchange + "-" + time_period + "-" + token + '-open-interest-' + 'usd' + '.csv', 'w') as f:
                f.write("date,value" + "\n")
                for key in data['time']:
                    t = data['time'][key][0:19]
                    f.write(t + "," + str(data['volume'][key]) + "\n")
        for key in emptyTokens:
            path = "static/js/open-interest/"
            with open(path + exchange + "-" + str(emptyTokens[key]) + "-" + key + '-open-interest-' + 'usd' + '.csv', 'w') as f:
                f.write("date,value" + "\n")
    
    emptyTokens = {}
    for time_period in time:
        for token in tokens: 
            #bitmex_query = f"select * from exchange_open_interest where time>= now() - {time_period}"
            bitmex_query = f"select coin_denominated_open_interest,contract_symbol from exchange_open_interest where time >= now() - {time_period} and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if len(data) == 0:
                emptyTokens[token] = time_period
                continue
            df = df.fillna(method='bfill')
            path = "static/js/open-interest/"
            with open(path + exchange + "-" + time_period + "-" + token + '-open-interest-coin.csv', 'w') as f:
                f.write("date,value" + "\n")
                for key in data['time']:
                    t = data['time'][key][0:19]
                    if(data['coin_denominated_open_interest'][key] == 0):
                        continue
                    f.write(t + "," + str(data['coin_denominated_open_interest'][key]) + "\n")
    for key in emptyTokens:
        path = "static/js/open-interest/"
        with open(path + exchange + "-" + str(emptyTokens[key]) + "-" + key + '-open-interest-coin.csv', 'w') as f:
            f.write("date,value" + "\n")

def huobi_volume():
    s = []
    emptyTokens={}
    exchange = 'huobi'
    coins = ['BTC', 'ETH', 'TRX', 'BSV', 'XRP', 'BCH', 'EOS', 'ETC', 'LTC']
    tokens = []
    for coin in coins:
        tokens.append(coin + weekly)
        tokens.append(coin + biweekly)
        tokens.append(coin + quarterly)
        tokens.append(coin + '-USD')

    time = ["1h", "2h", "12h", "1d"]
    for time_period in time:
        open_interest={}
        for token in tokens:
            bitmex_query = f"select vol,contract_code from huobidm_orderbook where time >= now() - {time_period} and contract_code =~ /{token}/"
            df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
            df = df.rename(columns={'first': 'open_interest'})
            data = df.to_dict()     
            if len(data) == 0:
                emptyTokens[token] = time_period
                continue       
            df = df.fillna(method='bfill')
            path = "static/js/volume/"
            with open(path + exchange + "-" + time_period + "-" + token + '-volume-' + '.csv', 'w') as f:
                f.write("date,value" + "\n")
                for key in data['time']:
                    t = data['time'][key][0:19]
                    f.write(t + "," + str(data['vol'][key]) + "\n")
        for key in emptyTokens:
            path = "static/js/volume/"
            with open(path + exchange + "-" + str(emptyTokens[key]) + "-" + key + '-volume-' + '.csv', 'w') as f:
                f.write("date,value" + "\n")

def okex():
    exchange = 'okex'
    okex_oi = dict()

    s = []
    emptyTokens={}
    exchange = 'okex'
    coins = ['BTC', 'LTC', 'ETH', 'ETC', 'XRP', 'EOS', 'BCH', 'BSV', 'TRX']
    #coins = ['BTC', 'LTC', 'ETH', 'ETC', 'XRP', 'EOS', 'BCH', 'BSV', 'TRX', 'ADA', 'DASH', 'LINK', 'NEO', 'XTZ', 'ZEC']
    tokens = []
    for coin in coins:
        tokens.append(coin + '-USD-' + weekly)
        tokens.append(coin + '-USD-' + biweekly)
        tokens.append(coin + '-USD-' + quarterly)
        tokens.append(coin + '-USD-' + biquarterly)
        tokens.append(coin + '-USD-' + 'SWAP')
        tokens.append(coin + '-USDT-' + weekly)
        tokens.append(coin + '-USDT-' + biweekly)
        tokens.append(coin + '-USDT-' + quarterly)
        tokens.append(coin + '-USDT-' + biquarterly)
        tokens.append(coin + '-USDT-' + 'SWAP')

    #time = ["1h"]
    time = ["1h", "2h", "12h", "1d"]
    #time = ["1h"]

    emptyTokens = {}
    for time_period in time:
        for token in tokens: 
            bitmex_query = f"select usd_denominated_open_interest,coin_denominated_open_interest,contract_symbol from exchange_open_interest where time>= now() - {time_period}  and contract_exchange =~ /Okex/ and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()


            if len(data) == 0:
                path = "static/js/open-interest/"
                with open(path + exchange + "-" + time_period + "-" + token + '-open-interest-usd.csv', 'w') as f:
                    f.write("date,value" + "\n")
                with open(path + exchange + "-" + time_period + "-" + token + '-open-interest-coin.csv', 'w') as f:
                    f.write("date,value" + "\n")
                continue

            df = df.fillna(method='bfill')
            path = "static/js/open-interest/"
            with open(path + exchange + "-" + time_period + "-" + token + '-open-interest-usd.csv', 'w') as f:
                f.write("date,value" + "\n")
                for key in data['time']:
                    t = data['time'][key][0:19]
                    if(data['usd_denominated_open_interest'][key] == 0):
                        continue
                    f.write(t + "," + str(int(data['usd_denominated_open_interest'][key]) ) + "\n")
            
            with open(path + exchange + "-" + time_period + "-" + token + '-open-interest-coin.csv', 'w') as f:
                f.write("date,value" + "\n")
                for key in data['time']:
                    t = data['time'][key][0:19]
                    if(data['coin_denominated_open_interest'][key] == 0):
                        continue
                    f.write(t + "," + str(data['coin_denominated_open_interest'][key]) + "\n")

def binance():
    binance_oi = dict()
    exchange = 'binance'

    s = []
    emptyTokens={}
    tokens = ['LINKUSDT', 'ETHUSDT' ,'XMRUSDT' ,'BCHUSDT' ,'XTZUSDT' ,'BTCUSDT' ,'IOSTUSDT',
 'BNBUSDT' ,'EOSUSDT' ,'ZECUSDT' ,'ADAUSDT', 'IOTAUSDT', 'DASHUSDT', 'ATOMUSDT',
 'XRPUSDT', 'XLMUSDT' ,'LTCUSDT' ,'ETCUSDT', 'TRXUSDT' ,'NEOUSDT' ,'QTUMUSDT',
 'ONTUSDT' ,'BATUSDT' ,'VETUSDT']
    time = ["1h", "2h", "12h", "1d"]
    #time = ["1h", "2h", "12h", "1d", "3d" ]

    emptyTokens = {}
    for time_period in time:
        for token in tokens: 
            #bitmex_query = f"select * from exchange_open_interest where time>= now() - {time_period} and contract_exchange =~ /Binance/"
            bitmex_query = f"select usd_denominated_open_interest,contract_symbol from exchange_open_interest where time >= now() - {time_period} and contract_exchange =~ /Binance/ and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if len(data) == 0:
                emptyTokens[token] = time_period
                continue
            df = df.fillna(method='bfill')
            path = "static/js/open-interest/"
            with open(path + exchange + "-" + time_period + "-" + token + '-open-interest-usd.csv', 'w') as f:
                f.write("date,value" + "\n")
                for key in data['time']:
                    t = data['time'][key][0:19]
                    if(data['usd_denominated_open_interest'][key] == 0):
                        continue
                    f.write(t + "," + str(data['usd_denominated_open_interest'][key]) + "\n")
    for key in emptyTokens:
        path = "static/js/open-interest/"
        with open(path + exchange + "-" + str(emptyTokens[key]) + "-" + key + '-open-interest-usd.csv', 'w') as f:
            f.write("date,value" + "\n")
    

    emptyTokens = {}
    for time_period in time:
        for token in tokens: 
            #bitmex_query = f"select * from exchange_open_interest where time>= now() - {time_period}"
            bitmex_query = f"select coin_denominated_open_interest,contract_symbol from exchange_open_interest where time >= now() - {time_period} and contract_exchange =~ /Binance/ and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if len(data) == 0:
                emptyTokens[token] = time_period
                continue
            df = df.fillna(method='bfill')
            path = "static/js/open-interest/"
            with open(path + exchange + "-" + time_period + "-" + token + '-open-interest-coin.csv', 'w') as f:
                f.write("date,value" + "\n")
                for key in data['time']:
                    t = data['time'][key][0:19]
                    if(data['coin_denominated_open_interest'][key] == 0):
                        continue
                    f.write(t + "," + str(data['coin_denominated_open_interest'][key]) + "\n")
    for key in emptyTokens:
        path = "static/js/open-interest/"
        with open(path + exchange + "-" + str(emptyTokens[key]) + "-" + key + '-open-interest-coin.csv', 'w') as f:
            f.write("date,value" + "\n")
    

def ftx():
    exchange = 'FTX'

    s = []
    emptyTokens={}
    tokens = []
    coins = ["LINK", "ATOM", "XTZ", "BNB", "HT", "OKB", "BSV", "BCH", "BTC","ALT", "ETH", 'ETC', 'ALGO', 'EXCH', 'MATIC', 'LTC', 'LEO', 'XRP', 'ADA']

    for coin in coins:
        tokens.append(coin + "-PERP")
        tokens.append(coin + "-" + ftx_quarterly)
        if coin == "BTC":
            tokens.append(coin + "-" + ftx_biquarterly)

    time = ["1h", "2h", "12h", "1d"]
    #time = ["1h", "2h", "12h", "1d", "3d" ]


    emptyTokens = {}
    for time_period in time:
        for token in tokens: 
            #bitmex_query = f"select * from exchange_open_interest where time>= now() - {time_period} and contract_exchange  =~ /FTX/ "
            

            bitmex_query = f"select usd_denominated_open_interest,contract_symbol from exchange_open_interest where time >= now() - {time_period} and contract_exchange  =~ /FTX/ and contract_symbol =~ /{token}/"
            #pd.set_option('display.max_col', 500)
            df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if len(data) == 0:
                emptyTokens[token] = time_period
                continue
            df = df.fillna(method='bfill')
            path = "static/js/open-interest/"
            with open(path + exchange + "-" + time_period + "-" + token + '-open-interest-usd.csv', 'w') as f:
                f.write("date,value" + "\n")
                for key in data['time']:
                    t = data['time'][key][0:19]
                    if(data['usd_denominated_open_interest'][key] == 0 or data['contract_symbol'][key] != token):
                        continue
                    f.write(t + "," + str(data['usd_denominated_open_interest'][key]) + "\n")
    for key in emptyTokens:
        path = "static/js/open-interest/"
        with open(path + exchange + "-" + str(emptyTokens[key]) + "-" + key + '-open-interest-usd.csv', 'w') as f:
            f.write("date,value" + "\n")
    
    emptyTokens = {}
    for time_period in time:
        for token in tokens: 
            #bitmex_query = f"select * from exchange_open_interest where time>= now() - {time_period}"
            bitmex_query = f"select coin_denominated_open_interest,contract_symbol from exchange_open_interest where time >= now() - {time_period} and contract_symbol =~ /{token}/"
            #pd.set_option('display.max_col', 500)
            df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if len(data) == 0:
                emptyTokens[token] = time_period
                continue
            df = df.fillna(method='bfill')
            path = "static/js/open-interest/"
            with open(path + exchange + "-" + time_period + "-" + token + '-open-interest-coin.csv', 'w') as f:
                f.write("date,value" + "\n")
                for key in data['time']:
                    t = data['time'][key][0:19]
                    if(data['coin_denominated_open_interest'][key] == 0 or data['contract_symbol'][key] != token):
                        continue
                    f.write(t + "," + str(data['coin_denominated_open_interest'][key]) + "\n")
    for key in emptyTokens:
        path = "static/js/open-interest/"
        with open(path + exchange + "-" + str(emptyTokens[key]) + "-" + key + '-open-interest-coin.csv', 'w') as f:
            f.write("date,value" + "\n")

def bybit():
    bybit_oi = dict()
    exchange = 'bybit'
    s = []
    emptyTokens={}
    tokens = ['BTCUSD' ,'ETHUSD' ,'EOSUSD', 'XRPUSD', 'BTCUSDT']
    time = ["1h", "2h", "12h", "1d"]
    #time = ["1h", "2h", "12h", "1d", "3d" ]
    
    for time_period in time:
        open_interest={}
        for token in tokens:
            okex = f"select open_interest,symbol from bybit_tickers where time >= now() - {time_period} and symbol =~ /{token}/"
            #okex = f"select usd_denominated_open_interest,contract_symbol from exchange_open_interest where time >= now() - {time_period} and contract_exchange = Bybit and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(okex, chunked=True, chunk_size=10000).get_points())
            df = df.rename(columns={'first': 'open_interest'})
            pd.set_option('display.max_rows', 500)
            data = df.to_dict()
            if len(data) == 0:
                emptyTokens[token] = time_period
                continue

            df = df.fillna(method='bfill')
            path = "static/js/open-interest/"
            with open(path + exchange + "-" + time_period + "-" + token + '-open-interest-' + 'usd' + '.csv', 'w') as f:
                f.write("date,value" + "\n")
                for key in data['time']:
                    t = data['time'][key][0:19]
                    if(data['open_interest'][key] == 0 or data['open_interest'][key] > 60000000000 or data['symbol'][key] != token):
                        continue
                    f.write(t + "," + str(data['open_interest'][key]) + "\n")

    for key in emptyTokens:
        path = "static/js/open-interest/"
        with open(path + exchange + "-" + str(emptyTokens[key]) + "-" + key + '-open-interest-' + 'usd' + '.csv', 'w') as f:
            f.write("date,value" + "\n")
    
def deribit():
    exchange = 'deribit'
    emptyTokens={}
    tokens = []
    coins = ['BTC-', 'ETH-']
    for coin in coins:
        tokens.append(coin + deribit_quarterly)
        tokens.append(coin + deribit_biquarterly)
        tokens.append(coin + deribit_semi)
        tokens.append(coin + "PERPETUAL")

    time = ["1h", "2h", "12h", "1d"]
    #time = ["1h", "2h", "12h", "1d", "3d" ]
    
    for time_period in time:
        open_interest={}
        for token in tokens:
            okex = f"select usd_denominated_open_interest,contract_symbol from exchange_open_interest where time >= now() - {time_period} and contract_exchange =~ /Deribit/ and contract_symbol =~ /{token}/"
            #okex = f"select usd_denominated_open_interest,contract_symbol from exchange_open_interest where time >= now() - {time_period} and contract_exchange = Bybit and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(okex, chunked=True, chunk_size=10000).get_points())
            print(time_period, token)
            print(df)
            df = df.rename(columns={'first': 'open_interest'})
            pd.set_option('display.max_columns', 500)
            data = df.to_dict()
            if len(data) == 0:
                emptyTokens[token] = time_period
                continue

            df = df.fillna(method='bfill')
            path = "static/js/open-interest/"
            with open(path + exchange + "-" + time_period + "-" + token + '-open-interest-' + 'usd' + '.csv', 'w') as f:
                f.write("date,value" + "\n")
                for key in data['time']:
                    t = data['time'][key][0:19]
                    if(data['usd_denominated_open_interest'][key] == 0 or data['contract_symbol'][key] != token):
                        continue
                    f.write(t + "," + str(data['usd_denominated_open_interest'][key]) + "\n")

    for key in emptyTokens:
        path = "static/js/open-interest/"
        with open(path + exchange + "-" + str(emptyTokens[key]) + "-" + key + '-open-interest-' + 'usd' + '.csv', 'w') as f:
            f.write("date,value" + "\n")
    
    for time_period in time:
        open_interest={}
        for token in tokens:
            okex = f"select coin_denominated_open_interest,contract_symbol from exchange_open_interest where time >= now() - {time_period} and contract_exchange =~ /Deribit/ and contract_symbol =~ /{token}/"
            #okex = f"select usd_denominated_open_interest,contract_symbol from exchange_open_interest where time >= now() - {time_period} and contract_exchange = Bybit and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(okex, chunked=True, chunk_size=10000).get_points())
            df = df.rename(columns={'first': 'open_interest'})
            pd.set_option('display.max_rows', 500)
            data = df.to_dict()
            if len(data) == 0:
                emptyTokens[token] = time_period
                continue

            df = df.fillna(method='bfill')
            path = "static/js/open-interest/"
            with open(path + exchange + "-" + time_period + "-" + token + '-open-interest-' + 'coin' + '.csv', 'w') as f:
                f.write("date,value" + "\n")
                for key in data['time']:
                    t = data['time'][key][0:19]
                    if(data['coin_denominated_open_interest'][key] == 0 or data['contract_symbol'][key] != token):
                        continue
                    f.write(t + "," + str(data['coin_denominated_open_interest'][key]) + "\n")

    for key in emptyTokens:
        path = "static/js/open-interest/"
        with open(path + exchange + "-" + str(emptyTokens[key]) + "-" + key + '-open-interest-' + 'coin' + '.csv', 'w') as f:
            f.write("date,value" + "\n")

def find_open_interest():
    bitmex()
    print("bitmex - oi")
    binance()
    print("binance - oi")
    okex()
    print("okex - oi")
    ftx()
    print("ftx - oi")
    bybit()
    print("bybit - oi")
    huobi()
    print("huobi - oi")
    deribit()
    print("deribit - oi")

def find_liquidation_bitmex():
    time = ["1d", "3d"]
    tokens = ['XBTUSD', 'XBTM20', 'XBTU20' , 'ETHUSD', 'ETHM20', 'BCHM20', 'TRXM20', 'LTCM20', 'ADAM20', 'XRPUSD', 'EOSM20']
    #time = ['1d']
    #tokens = ['XBTUSD']
    for time_period in time:
        emptyTokens = []
        liquidations = {}
        prevHr = 0
        hours = {}
        currHour = 0
        val = 0
        counter = 0
        for token in tokens:
            liquidation_query = f"select * from bitmex_liquidation where time >= now() - {time_period} and symbol =~ /{token}/"
            df = pd.DataFrame(client.query(liquidation_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if len(data) == 0:
                emptyTokens.append(token)
                continue
            
            currHour = data['time'][0][11:13]
            prevHour = currHour
            token_liquidations = {'Buy':{},'Sell':{}}
            for key in data['time']:
                t = data['time'][key][0: 19]
                token_liquidations[data['side'][key]][t] = data['leavesQty'][key]

                currHour = data['time'][key][11:13]
                if( currHour != prevHour):
                    hours[t[0:11] + prevHour + ':00:00'] = val
                    val = data['leavesQty'][key]
                    prevHour = currHour
                else: 
                    val =  val + data['leavesQty'][key]

            liquidations[token] = token_liquidations
        for token in liquidations.keys():
            path = "static/js/liquidations/"
            with open(path + 'bitmex-' + time_period + "-" + token + '-liquidations.csv', 'w') as f:
                f.write("Hrs,Liq," + "BuySell" + '\n')
                for buyOrSell in liquidations[token].keys():
                    for hrsAgo in liquidations[token][buyOrSell].keys():
                        f.write(hrsAgo + "," + str(liquidations[token][buyOrSell][hrsAgo]) + "," + buyOrSell + "\n")
            with open(path + 'bitmex-' +  time_period + '-' + token + '-hours.csv' , 'w') as f:
                f.write("Hrs,Liq" + "\n")
                for time in hours:
                    f.write(time + "," + str(hours[time]) + "\n")
        if (len(emptyTokens)!=0):
            for token in emptyTokens:
                path = "static/js/liquidations/"
                with open(path + 'bitmex-' + time_period + "-" + token + '-liquidations.csv', 'w') as f:
                    f.write("Hrs,Liq," + "BuySell" + '\n')

def find_liquidation_okex():
    # 4 is buy, 3 is sell
    time = ["1d", "3d"]
    tokens = ['BTC-USDT-SWAP', 'BTC-USD-SWAP' ,'BCH-USDT-SWAP', 'BCH-USD-SWAP',
    'LINK-USDT-SWAP', 'LINK-USD-SWAP' ,'BSV-USDT-SWAP' ,'ETH-USD-SWAP',
    'BSV-USD-SWAP' ,'ETH-USDT-SWAP' ,'EOS-USD-SWAP', 'XRP-USD-SWAP',
    'EOS-USDT-SWAP', 'LTC-USD-SWAP' ,'TRX-USD-SWAP' ,'XRP-USDT-SWAP',
    'LTC-USDT-SWAP' ,'TRX-USDT-SWAP' ,'NEO-USD-SWAP' ,'DASH-USDT-SWAP']
    for time_period in time:
        emptyTokens = []
        liquidations = {}
        prevHr = 0
        hours = {}
        currHour = 0
        val = 0
        for token in tokens:
            liquidation_query = f"select * from okex_liquidation where time >= now() - {time_period} and symbol =~ /{token}/"
            df = pd.DataFrame(client.query(liquidation_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            
            if len(data) == 0:
                emptyTokens.append(token)
                continue

            currHour = data['time'][0][11:13]
            prevHour = currHour
            token_liquidations = {'Buy':{},'Sell':{}}
            for key in data['time']:
                t = data['time'][key][0: 19]

                if data['type'][key] == '4':
                    token_liquidations['Buy'][t] = data['size'][key]
                else:
                    token_liquidations['Sell'][t] = data['size'][key]   

                currHour = data['time'][key][11:13]
                if( currHour != prevHour):
                    hours[t[0:11] + prevHour + ':00:00'] = val
                    val = int(data['size'][key])
                    prevHour = currHour
                else: 
                    val =  val + int(data['size'][key])

            liquidations[token] = token_liquidations
        for token in liquidations.keys():
            path = "static/js/liquidations/"
            with open(path +  'okex-' + time_period + "-" + token + '-liquidations.csv', 'w') as f:
                f.write("Hrs,Liq," + "BuySell" + '\n')
                for buyOrSell in liquidations[token].keys():
                    for hrsAgo in liquidations[token][buyOrSell].keys():
                        f.write(hrsAgo + "," + str(liquidations[token][buyOrSell][hrsAgo]) + "," + buyOrSell + "\n")
            with open(path + 'okex-' + time_period + '-' + token + '-hours.csv' , 'w') as f:
                f.write("Hrs,Liq" + "\n")
                for time in hours:
                    f.write(time + "," + str(hours[time]) + "\n")
        if (len(emptyTokens)!=0):
            for token in emptyTokens:
                path = "static/js/liquidations/"
                with open(path + 'okex-' + time_period + "-" + token + '-liquidations.csv', 'w') as f:
                    f.write("Hrs,Liq," + "BuySell" + '\n')

def find_liquidation_binance():
    time = ["1d", "3d"]
    tokens = ['LINKUSDT', 'ETHUSDT' ,'XMRUSDT' ,'BCHUSDT' ,'XTZUSDT' ,'BTCUSDT' ,'IOSTUSDT',
 'BNBUSDT' ,'EOSUSDT' ,'ZECUSDT' ,'ADAUSDT', 'IOTAUSDT', 'DASHUSDT', 'ATOMUSDT',
 'XRPUSDT', 'XLMUSDT' ,'LTCUSDT' ,'ETCUSDT', 'TRXUSDT' ,'NEOUSDT' ,'QTUMUSDT',
 'ONTUSDT' ,'BATUSDT' ,'VETUSDT']
    for time_period in time:
        emptyTokens = []
        liquidations = {}
        prevHour = 0
        hours = {}
        currHour = 0
        val = 0
        for token in tokens:
            liquidation_query = f"select * from binance_liquidation_trades where time >= now() - {time_period} and symbol =~ /{token}/"
            df = pd.DataFrame(client.query(liquidation_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if len(data) == 0:
                emptyTokens.append(token)
                continue

            token_liquidations = {'Buy':{},'Sell':{}}
            for key in data['time']:
                t = data['time'][key][0: 19]
                #print(data['side'])
                if data['side'][key] == 'BUY':
                    token_liquidations['Buy'][t] = data['executedQty'][key]
                else:
                    token_liquidations['Sell'][t] = data['executedQty'][key]                
                
                currHour = data['time'][key][11:13]
                if( currHour != prevHour):
                    hours[str(t[0:11]) + str(prevHour) + ':00:00'] = val
                    val = data['executedQty'][key]
                    prevHour = currHour
                else: 
                    val =  val + data['executedQty'][key]
                    
            liquidations[token] = token_liquidations

        for token in liquidations.keys():
            path = "static/js/liquidations/"
            with open(path + 'binance-' + time_period + "-" + token + '-liquidations.csv', 'w') as f:
                f.write("Hrs,Liq," + "BuySell" + '\n')
                for buyOrSell in liquidations[token].keys():
                    for hrsAgo in liquidations[token][buyOrSell].keys():
                        f.write(hrsAgo + "," + str(liquidations[token][buyOrSell][hrsAgo]) + "," + buyOrSell + "\n")
            with open(path + 'binance-' +  time_period + '-' + token + '-hours.csv' , 'w') as f:
                f.write("Hrs,Liq" + "\n")
                for time in hours:
                    f.write(time + "," + str(hours[time]) + "\n")
        if (len(emptyTokens)!=0):
            for token in emptyTokens:
                path = "static/js/liquidations/"
                with open(path + 'binance-' + time_period + "-" + token + '-liquidations.csv', 'w') as f:
                    f.write("Hrs,Liq," + "BuySell" + '\n')

def find_liquidation_ftx():
    time = ["1d", "3d"]
    tokens = ["LINK-PERP", "ATOM-PERP", "XTZ-PERP", "BNB-PERP", "HT-PERP", "OKB-PERP", "BSV-PERP", "BCH-PERP", "BTC-PERP","ALT-PERP", "ETH-PERP"]

    for time_period in time:
        emptyTokens = []
        liquidations = {}
        prevHour = 0
        hours = {}
        currHour = 0
        val = 0
        for token in tokens:
            liquidation_query = f"select * from FTX_trades where time >= now() - {time_period} and symbol =~ /{token}/"
            df = pd.DataFrame(client.query(liquidation_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if len(data) == 0:
                emptyTokens.append(token)
                continue

            token_liquidations = {'Buy':{},'Sell':{}}
            for key in data['time']:
                t = data['time'][key][0: 19]
                if data['side'][key] == 'buy':
                    token_liquidations['Buy'][t] = data['size'][key]
                else:
                    token_liquidations['Sell'][t] = data['size'][key]                
                
                currHour = data['time'][key][11:13]
                if( currHour != prevHour):
                    hours[str(t[0:11]) + str(prevHour) + ':00:00'] = val
                    val = data['size'][key]
                    prevHour = currHour
                else: 
                    val =  val + data['size'][key]
                    
            liquidations[token] = token_liquidations

        for token in liquidations.keys():
            path = "static/js/liquidations/"
            with open(path + 'ftx-' + time_period + "-" + token + '-liquidations.csv', 'w') as f:
                f.write("Hrs,Liq," + "BuySell" + '\n')
                for buyOrSell in liquidations[token].keys():
                    for hrsAgo in liquidations[token][buyOrSell].keys():
                        f.write(hrsAgo + "," + str(liquidations[token][buyOrSell][hrsAgo]) + "," + buyOrSell + "\n")
            with open(path + 'ftx-' +  time_period + '-' + token + '-hours.csv' , 'w') as f:
                f.write("Hrs,Liq" + "\n")
                for time in hours:
                    f.write(time + "," + str(hours[time]) + "\n")
        if (len(emptyTokens)!=0):
            for token in emptyTokens:
                path = "static/js/liquidations/"
                with open(path + 'ftx-' + time_period + "-" + token + '-liquidations.csv', 'w') as f:
                    f.write("Hrs,Liq," + "BuySell" + '\n')

def open_interest_price_bitmex():
    #Testing price/OI variations for 12h BTC price vs bitmex XBTUSD OI normalized to USD
    #CSV file: price/open-interest, time, value
    #CSV file: time, price, OI
    
    time = ["1h", "2h", "12h", "1d"]
    
    tokens = ['XBTUSD', 'XBTM20', 'XBTU20' , 'ETHUSD', 'BCHM20', 'TRXM20', 'ETHM20', 'LTCM20', 'ADAM20', 'XRPUSD', 'XRPM20', 'EOSM20']
    for token in tokens:
        for time_period in time:
            #bitmex_query = f"select * from bitmex_trade where time >= now() - 12h"
            bitmex_query = f"select price,symbol from bitmex_trade where time >= now() - {time_period} and symbol =~ /{token}/"
            df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()

            path = "static/js/open-interest-price/"
            with open(path + 'bitmex' + "-" + time_period + "-" + token + '-open-interest-price.csv', 'w') as f:
                f.write("date,price" + "\n")
                for key in data['time']:
                    t = data['time'][key][0:19]
                    f.write(t + "," + str(data['price'][key]) + "\n")

def open_interest_price_btc():
    #Testing price/OI variations for 12h BTC price vs bitmex XBTUSD OI normalized to USD
    #CSV file: price/open-interest, time, value
    #CSV file: time, price, OI
    
    time = ["1h", "2h", "12h", "1d", "3d", "7d"]
    
    for time_period in time:
        #bitmex_query = f"select * from bitmex_trade where time >= now() - 12h"
        bitmex_query = f"select price,symbol from bitmex_trade where time >= now() - {time_period} and symbol =~ /XBTUSD/"
        df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
        print(time_period,'XBTUSD')
        print(df)
        data = df.to_dict()
        if(len(data) == 0):
            path = "static/js/open-interest-price/"
            with open(path + "XBTUSD" + "-" + time_period + '-open-interest-price.csv', 'w') as f:
                f.write("date,price" + "\n")
            continue

        path = "static/js/open-interest-price/"
        with open(path + 'XBTUSD' + "-" + time_period + "-open-interest-price.csv", 'w') as f:
            f.write("date,price" + "\n")
            for key in data['time']:
                t = data['time'][key][0:19]
                f.write(t + "," + str(data['price'][key]) + "\n")
        
        done = {}

    for time_period in time:

        bitmex_query = f"select price,symbol from bitmex_trade where time >= now() - {time_period} and symbol =~ /ETHUSD/"
        df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
        print(time_period,'ETHUSD')
        print(df)
        data = df.to_dict()
        if(len(data) == 0):
            print(time_period,'ETHUSD')
            path = "static/js/open-interest-price/"
            with open(path + "ETHUSD" + "-" + time_period + '-open-interest-price.csv', 'w') as f:
                f.write("date,price" + "\n")
            continue

        path = "static/js/open-interest-price/"
        with open(path + 'ETHUSD' + "-" + time_period + "-open-interest-price.csv", 'w') as f:
            f.write("date,price" + "\n")
            for key in data['time']:
                t = data['time'][key][0:15]
                t += "0:00"
                if 'ETHUSD' in done and done['ETHUSD'] == t:
                    continue
                else:
                    done['ETHUSD'] = t
                if data['symbol'][key] != 'ETHUSD':
                    continue
                f.write(t + "," + str(data['price'][key]) + "\n")
    
def open_interest_price_okex():   
    time = ["1h", "2h", "12h", "1d"]
    coins = ['BTC', 'LTC', 'ETH', 'ETC', 'XRP', 'EOS', 'BCH', 'BSV', 'TRX']
    #coins = ['BTC', 'LTC', 'ETH', 'ETC', 'XRP', 'EOS', 'BCH', 'BSV', 'TRX', 'ADA', 'DASH', 'LINK', 'NEO', 'XTZ', 'ZEC']
    tokens = []
    emptyTokens = {}
    for coin in coins:
        tokens.append(coin + '-USD-' + weekly)
        tokens.append(coin + '-USD-' + biweekly)
        tokens.append(coin + '-USD-' + quarterly)
        tokens.append(coin + '-USD-' + biquarterly)
        tokens.append(coin + '-USD-' + 'SWAP')
        tokens.append(coin + '-USDT-' + weekly)
        tokens.append(coin + '-USDT-' + biweekly)
        tokens.append(coin + '-USDT-' + quarterly)
        tokens.append(coin + '-USDT-' + biquarterly)
        tokens.append(coin + '-USDT-' + 'SWAP')
    for token in tokens:
        for time_period in time:
            #okex_query = f"select * from okex_recentTrades_clean where time >= now() - 1h"
            okex_query = f"select price,symbol from okex_recentTrades_clean where time >= now() - {time_period} and symbol =~ /{token}/"
            df = pd.DataFrame(client.query(okex_query, chunked = True, chunk_size = 10000).get_points())
            data = df.to_dict()
            if (len(data) == 0):
                path = "static/js/open-interest-price/"
                with open(path + "okex" + "-" + time_period + "-" + token + '-open-interest-price.csv', 'w') as f:
                    f.write("date,price" + "\n")
                continue
            
            path = "static/js/open-interest-price/"
            with open(path + 'okex' + "-" + time_period + "-" + token + '-open-interest-price.csv', 'w') as f:
                f.write("date,price" + "\n")
                for key in data['time']:
                    t = data['time'][key][0:19]
                    f.write(t + "," + str(data['price'][key]) + "\n")

    for key in emptyTokens:
        path = "static/js/open-interest-price/"
        with open(path + "okex" + "-" + str(emptyTokens[key]) + "-" + key + '-open-interest-price.csv', 'w') as f:
            f.write("date,price" + "\n")
        
def stack_open_interest():
    # Stacked graphs for bitmex XBTUSD OI and okex BTC-USD-SWAP OI
    # CSV format: date, xbtusd .... zec-usdt-swap
    max_value = 0
    min_value = float('inf')
    
    counter = 0
    coins = ['BTC', 'LTC', 'ETH', 'ETC', 'XRP', 'EOS', 'BCH', 'BSV', 'TRX']
    #coins = ['BTC', 'LTC', 'ETH', 'ETC', 'XRP', 'EOS', 'BCH', 'BSV', 'TRX', 'ADA', 'DASH', 'LINK', 'NEO', 'XTZ', 'ZEC']
    okex_tokens = []
    for coin in coins:
        okex_tokens.append(coin + '-USD-' + weekly)
        okex_tokens.append(coin + '-USD-' + biweekly)
        okex_tokens.append(coin + '-USD-' + quarterly)
        okex_tokens.append(coin + '-USD-' + biquarterly)
        okex_tokens.append(coin + '-USD-' + 'SWAP')
        okex_tokens.append(coin + '-USDT-' + weekly)
        okex_tokens.append(coin + '-USDT-' + biweekly)
        okex_tokens.append(coin + '-USDT-' + quarterly)
        okex_tokens.append(coin + '-USDT-' + biquarterly)
        okex_tokens.append(coin + '-USDT-' + 'SWAP')

    #time = ["1h"]
    time = ["2h"]
    #time = ["1h"]
    done = {}
    bitmex_tokens = ['XBTUSD', 'XBTM20', 'XBTU20' , 'ETHUSD', 'BCHM20', 'TRXM20', 'ETHM20', 'LTCM20', 'ADAM20', 'XRPUSD', 'XRPM20', 'EOSM20']

    path = "static/js/open-interest/"
    date = []
    dictionary = {}
    done = {}
    for token in bitmex_tokens:
        temp = []
        bitmex_query = f"select openInterest,symbol from bitmex_instrument where time >= now() - 6h and symbol =~ /{token}/"
        df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
        data = df.to_dict()
        if len(data) == 0:
            continue
        df = df.fillna(method='bfill')
        for key in data['time']:
            t = data['time'][key][0:15]
            t += "0"
            if token in done and done[token] == t:
                continue
            else:
                done[token] = t
            if(data['openInterest'][key] == 0):
                continue
            temp.append(str(int(data['openInterest'][key])))
            date.append(t)
    dictionary['date'] = date

    for token in bitmex_tokens:
        temp = []
        bitmex_query = f"select openInterest,symbol from bitmex_instrument where time >= now() - 6h and symbol =~ /{token}/"
        df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
        data = df.to_dict()
        if len(data) == 0:
            continue
        df = df.fillna(method='bfill')
        for key in data['time']:
            t = data['time'][key][0:15]
            t += "0"
            if token in done and done[token] == t:
                continue
            else:
                done[token] = t
            if(data['openInterest'][key] == 0):
                continue
            temp.append(str(int(data['openInterest'][key])))
            if data['openInterest'][key] > max_value:
                max_value = data['openInterest'][key]
            if data['openInterest'][key] < min_value:
                min_value = data['openInterest'][key]
            date.append(t)
        dictionary[token] = temp

    for token in okex_tokens:
        temp = []
        okex_query = f"select usd_denominated_open_interest,contract_symbol from exchange_open_interest where time>= now() - 12h  and contract_exchange =~ /Okex/ and contract_symbol =~ /{token}/"
        df = pd.DataFrame(client.query(okex_query, chunked=True, chunk_size=10000).get_points())
        data = df.to_dict()
        if len(data) == 0:
            print(token)
            continue
        df = df.fillna(method='bfill')
        print(token)
        print(df)
        for key in data['time']:
            t = data['time'][key][0:15]
            t += "0"
            if token in done and done[token] == t:
                continue
            else:
                done[token] = t
            if(data['usd_denominated_open_interest'][key] == 0):
                continue
            temp.append(str(int(data['usd_denominated_open_interest'][key])))
            if data['usd_denominated_open_interest'][key] > max_value:
                max_value = data['usd_denominated_open_interest'][key]
            if data['usd_denominated_open_interest'][key] < min_value:
                min_value = data['usd_denominated_open_interest'][key]
            date.append(t)
        dictionary[token] = temp

    with open(path + 'stacked-open-interest-usd.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(dictionary.keys())
        writer.writerows(zip(*dictionary.values()))
    print(min_value,max_value)
    return max_value,min_value

def btc_eth_open_interest(data):
    min_value = float('inf')
    max_value = 0
    path = "static/js/open-interest/"
    date = []
    dictionary = {}
    done = {}

    bitmex = ['XBTUSD','ETHUSD']
    okex = ['BTC-USD-SWAP','ETH-USD-SWAP']
    okex.append('BTC-USD-' + weekly)
    okex.append('BTC-USD-' + biweekly)
    okex.append('BTC-USD-' + quarterly)
    okex.append('BTC-USD-' + biquarterly)

    huobi = ['BTC-USD','ETH-USD']
    binance = ['BTCUSDT','ETHUSDT']
    bybit = ['BTCUSD', 'ETHUSD']
    ftx = ['BTC-PERP','ETH-PERP']

    for i in range(len(data)):
        if data[i] == "BTC weekly":
            data[i] = "BTC-USD-" + weekly
        if data[i]== "BTC biweekly":
            data[i]= "BTC-USD-" + biweekly
        if data[i]== "BTC quarterly":
            data[i]= "BTC-USD-" + quarterly
        if data[i]== "BTC biquarterly":
            data[i]= "BTC-USD-" + biquarterly
    
    bitmex_tokens = []
    okex_tokens = []
    huobi_tokens = []
    binance_tokens = []
    bybit_tokens = []
    ftx_tokens = []

    time = ["1h", "2h", "12h", "1d" , "3d", "7d"]
    date_bool = False

    for token in data:
        if token in bitmex:
            bitmex_tokens.append(token)
        if token in okex:
            okex_tokens.append(token)
        if token in huobi:
            huobi_tokens.append(token)
        if token in binance:
            binance_tokens.append(token)
        if token in bybit:
            bybit_tokens.append(token)
        if token in ftx:
            ftx_tokens.append(token)
    
    for time_period in time:
        dictionary = {}

        for token in bitmex_tokens:
            temp = []
            done = {}
            date = []
            bitmex_query = f"select usd_denominated_open_interest,contract_symbol from exchange_open_interest where time>= now() - {time_period}  and contract_exchange =~ /Bitmex/ and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
            print(time_period, token)
            print(df)
            data = df.to_dict()
            if len(data) == 0:
                continue
            df = df.fillna(method='bfill')
            for key in data['time']:
                t = data['time'][key][0:15]
                t += "0:00"
                if token in done and done[token] == t:
                    continue
                else:
                    done[token] = t
                if(data['usd_denominated_open_interest'][key] == 0 or data['contract_symbol'][key] != token):
                    continue
                temp.append(str(int(data['usd_denominated_open_interest'][key])))
                if data['usd_denominated_open_interest'][key] > max_value:
                    max_value = data['usd_denominated_open_interest'][key]
                if data['usd_denominated_open_interest'][key] < min_value:
                    min_value = data['usd_denominated_open_interest'][key]
                date.append(t)
            if len(bitmex) !=0:
                dictionary['date'] = date
                date_bool = True
            dictionary[token] = temp

        for token in okex_tokens:
            temp = []
            done = {}
            date = []            
            okex_query = f"select usd_denominated_open_interest,contract_symbol from exchange_open_interest where time>= now() - {time_period}  and contract_exchange =~ /Okex/ and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(okex_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            print(time_period,token)
            print(df)
            if len(data) == 0:
                print(token)
                continue
            df = df.fillna(method='bfill')
            for key in data['time']:
                t = data['time'][key][0:15]
                t += "0:00"                
                if token in done and done[token] == t:
                    continue
                else:
                    done[token] = t
                if(data['usd_denominated_open_interest'][key] == 0):
                    continue
                temp.append((int(data['usd_denominated_open_interest'][key])))
                if data['usd_denominated_open_interest'][key] > max_value:
                    max_value = data['usd_denominated_open_interest'][key]
                if data['usd_denominated_open_interest'][key] < min_value:
                    min_value = data['usd_denominated_open_interest'][key]
                date.append(t)
            if not (date_bool):
                dictionary['date'] = date
            dictionary[token] = temp
        
        for token in huobi_tokens:
            temp = []
            done = {}
            date = []            
            huobi_query =  f"select usd_denominated_open_interest,coin_denominated_open_interest,contract_symbol from exchange_open_interest where time>= now() - {time_period}  and contract_exchange =~ /Huobi/ and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(huobi_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if len(data) == 0:
                print(token)
                continue
            df = df.fillna(method='bfill')
            for key in data['time']:
                t = data['time'][key][0:15]
                t += "0:00"
                if token in done and done[token] == t:
                    continue
                else:
                    done[token] = t
                if(data['usd_denominated_open_interest'][key] == 0):
                    continue
                temp.append((int(data['usd_denominated_open_interest'][key])))
                if data['usd_denominated_open_interest'][key] > max_value:
                    max_value = data['usd_denominated_open_interest'][key]
                if data['usd_denominated_open_interest'][key] < min_value:
                    min_value = data['usd_denominated_open_interest'][key]
                date.append(t)
            if not (date_bool):
                dictionary['date'] = date
            dictionary[token] = temp

        for token in binance_tokens:
            temp = []
            done = {}
            date = []            
            binance_query = f"select usd_denominated_open_interest,contract_symbol from exchange_open_interest where time >= now() - {time_period} and contract_exchange =~ /Binance/ and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(binance_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if len(data) == 0:
                print(token)
                continue
            df = df.fillna(method='bfill')
            for key in data['time']:
                t = data['time'][key][0:15]
                t += "0:00"
                if token in done and done[token] == t:
                    continue
                else:
                    done[token] = t
                if(data['usd_denominated_open_interest'][key] == 0):
                    continue
                temp.append((int(data['usd_denominated_open_interest'][key])))
                if data['usd_denominated_open_interest'][key] > max_value:
                    max_value = data['usd_denominated_open_interest'][key]
                if data['usd_denominated_open_interest'][key] < min_value:
                    min_value = data['usd_denominated_open_interest'][key]
                date.append(t)
            if not (date_bool):
                dictionary['date'] = date
            dictionary[token] = temp

        for token in bybit_tokens:
            temp = []
            done = {}
            date = []            
            bybit_query = f"select open_interest,symbol from bybit_tickers where time >= now() - {time_period} and symbol =~ /{token}/"
            df = pd.DataFrame(client.query(bybit_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if len(data) == 0:
                print(token)
                continue
            df = df.fillna(method='bfill')
            for key in data['time']:
                t = data['time'][key][0:15]
                t += "0:00"
                if token in done and done[token] == t:
                    continue
                else:
                    done[token] = t
                if(data['open_interest'][key] == 0):
                    continue
                temp.append((int(data['open_interest'][key])))
                if data['open_interest'][key] > max_value:
                    max_value = data['open_interest'][key]
                if data['open_interest'][key] < min_value:
                    min_value = data['open_interest'][key]
                date.append(t)
            if not (date_bool):
                dictionary['date'] = date
            dictionary[token] = temp
        
        for token in ftx_tokens:
            temp = []
            done = {}
            date = []            
            ftx_query = f"select usd_denominated_open_interest,contract_symbol from exchange_open_interest where time >= now() - {time_period} and contract_exchange  =~ /FTX/ and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(ftx_query, chunked=True, chunk_size=10000).get_points())
            print(time_period,token)
            print(df)
            data = df.to_dict()
            if len(data) == 0:
                print(token)
                continue
            df = df.fillna(method='bfill')
            for key in data['time']:
                t = data['time'][key][0:15]
                t += "0:00"
                if token in done and done[token] == t:
                    continue
                else:
                    done[token] = t
                if(data['usd_denominated_open_interest'][key] == 0):
                    continue
                temp.append((int(data['usd_denominated_open_interest'][key])))
                if data['usd_denominated_open_interest'][key] > max_value:
                    max_value = data['usd_denominated_open_interest'][key]
                if data['usd_denominated_open_interest'][key] < min_value:
                    min_value = data['usd_denominated_open_interest'][key]
                date.append(t)
            if not (date_bool):
                dictionary['date'] = date
            dictionary[token] = temp
            
        
        with open(path + time_period + '-btc-eth-open-interest-usd.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(dictionary.keys())
            writer.writerows(zip(*dictionary.values()))

    print(max_value,min_value)
    return max_value,min_value


def select_open_interest(data):
    coins = ['BTC', 'LTC', 'ETH', 'ETC', 'XRP', 'EOS', 'BCH', 'BSV', 'TRX']
    #coins = ['BTC', 'LTC', 'ETH', 'ETC', 'XRP', 'EOS', 'BCH', 'BSV', 'TRX', 'ADA', 'DASH', 'LINK', 'NEO', 'XTZ', 'ZEC']
    okex_tokens = []
    for coin in coins:
        okex_tokens.append(coin + '-USD-' + weekly)
        okex_tokens.append(coin + '-USD-' + biweekly)
        okex_tokens.append(coin + '-USD-' + quarterly)
        okex_tokens.append(coin + '-USD-' + biquarterly)
        okex_tokens.append(coin + '-USD-' + 'SWAP')
        okex_tokens.append(coin + '-USDT-' + weekly)
        okex_tokens.append(coin + '-USDT-' + biweekly)
        okex_tokens.append(coin + '-USDT-' + quarterly)
        okex_tokens.append(coin + '-USDT-' + biquarterly)
        okex_tokens.append(coin + '-USDT-' + 'SWAP')
    

    max_value = 0
    min_value = float('inf')

    #time = ["1h"]
    time = ["1h", "2h", "12h", "1d" , "3d", "7d"]
    #time = ["1h"]
    done = {}
    bitmex_tokens = ['XBTUSD', 'XBTM20', 'XBTU20' , 'ETHUSD', 'BCHM20', 'TRXM20', 'ETHM20', 'LTCM20', 'ADAM20', 'XRPUSD', 'XRPM20', 'EOSM20']

    path = "static/js/open-interest/"
    date = []
    dictionary = {}
    done = {}

    for i in range(len(data)):
        if data[i] == "BTC weekly":
            data[i] = "BTC-USD-" + weekly
        if data[i]== "BTC biweekly":
            data[i]= "BTC-USD-" + biweekly
        if data[i]== "BTC quarterly":
            data[i]= "BTC-USD-" + quarterly
        if data[i]== "BTC biquarterly":
            data[i]= "BTC-USD-" + biquarterly

        if data[i]== "ETH weekly":
            data[i]= "ETH-USD-" + weekly
        if data[i]== "ETH biweekly":
            data[i]= "ETH-USD-" + biweekly
        if data[i]== "ETH quarterly":
            data[i]= "ETH-USD-" + quarterly
        if data[i]== "ETH biquarterly":
            data[i]= "ETH-USD-" + biquarterly

        if data[i]== "XRP weekly":
            data[i]= "XRP-USD-" + weekly
        if data[i]== "XRP biweekly":
            data[i]= "XRP-USD-" + biweekly
        if data[i]== "XRP quarterly":
            data[i]= "XRP-USD-" + quarterly
        if data[i]== "XRP biquarterly":
            data[i]= "XRP-USD-" + biquarterly

        if data[i]== "LTC weekly":
            data[i]= "LTC-USD-" + weekly
        if data[i]== "LTC biweekly":
            data[i]= "LTC-USD-" + biweekly
        if data[i]== "LTC quarterly":
            data[i]= "LTC-USD-" + quarterly
        if data[i]== "LTC biquarterly":
            data[i]= "LTC-USD-" + biquarterly


    bitmex = []
    okex = []
    for token in data:
        if token in bitmex_tokens:
            bitmex.append(token)
        if token in okex_tokens:
            okex.append(token)


    for time_period in time:
        dictionary = {}

        for token in bitmex:
            temp = []
            done = {}
            date = []
            bitmex_query = f"select openInterest,symbol from bitmex_instrument where time >= now() - {time_period} and symbol =~ /{token}/"
            df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if len(data) == 0:
                continue
            df = df.fillna(method='bfill')
            for key in data['time']:
                t = data['time'][key][0:15]
                t += "0"
                if token in done and done[token] == t:
                    continue
                else:
                    done[token] = t
                if(data['openInterest'][key] == 0):
                    continue
                temp.append(str(int(data['openInterest'][key])))
                if data['openInterest'][key] > max_value:
                    max_value = data['openInterest'][key]
                if data['openInterest'][key] < min_value:
                    min_value = data['openInterest'][key]
                date.append(t)
            if len(bitmex) !=0:
                dictionary['date'] = date
            dictionary[token] = temp

        for token in okex:
            temp = []
            done = {}
            date = []            
            okex_query = f"select usd_denominated_open_interest,contract_symbol from exchange_open_interest where time>= now() - {time_period}  and contract_exchange =~ /Okex/ and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(okex_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if len(data) == 0:
                print(token)
                continue
            df = df.fillna(method='bfill')
            for key in data['time']:
                t = data['time'][key][0:15]
                t += "0"
                if token in done and done[token] == t:
                    continue
                else:
                    done[token] = t
                if(data['usd_denominated_open_interest'][key] == 0):
                    continue
                temp.append((int(data['usd_denominated_open_interest'][key])))
                if data['usd_denominated_open_interest'][key] > max_value:
                    max_value = data['usd_denominated_open_interest'][key]
                if data['usd_denominated_open_interest'][key] < min_value:
                    min_value = data['usd_denominated_open_interest'][key]
                date.append(t)
            if len(bitmex) == 0:
                dictionary['date'] = date
            dictionary[token] = temp
        
        with open(path + time_period + '-stacked-open-interest-usd.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(dictionary.keys())
            writer.writerows(zip(*dictionary.values()))

    print(max_value, min_value)
    return max_value,min_value


def coin_open_interest():

    time = ["1h", "2h", "12h", "1d", "3d", "7d"]
    #coins = ["BSV"]
    coins = ["BTC", "ETH", "XRP", "BCH", "BSV", "LTC", "BNB", "TRX", "EOS"]
    temp = []
    temp_2 = []

    for coin in coins:
        max_value = 0
        min_value = float('inf')
        max_coin = 0
        min_coin = float('inf')

        for time_period in time:
            date_bool = False
            done = {}

            path = "static/js/open-interest/"
            date = []
            dictionary = {}
            dictionary_coin = {}
            done = {}

            token = coin + "USDT"

            binance_query = f"select usd_denominated_open_interest,coin_denominated_open_interest,contract_symbol from exchange_open_interest where time >= now() - {time_period} and contract_exchange =~ /Binance/ and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(binance_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if(len(data) != 0):
                df = df.fillna(method='bfill')
                temp = []
                temp_2 = []
                for key in data['time']:
                    t = data['time'][key][0:15]
                    t += "0"
                    if token in done and done[token] == t:
                        continue
                    else:
                        done[token] = t
                    if(data['usd_denominated_open_interest'][key] == 0 or data['coin_denominated_open_interest'][key] == 0):
                        continue
                    temp.append((int(data['usd_denominated_open_interest'][key])))
                    temp_2.append((int(data['coin_denominated_open_interest'][key])))
                    if data['usd_denominated_open_interest'][key] > max_value:
                        max_value = data['usd_denominated_open_interest'][key]
                    if data['usd_denominated_open_interest'][key] < min_value:
                        min_value = data['usd_denominated_open_interest'][key]
                    
                    if data['coin_denominated_open_interest'][key] > max_coin:
                        max_coin = data['coin_denominated_open_interest'][key]
                    if data['coin_denominated_open_interest'][key] < min_coin:
                        min_coin = data['coin_denominated_open_interest'][key]
                    date.append(t)
                dictionary['date'] = date
                dictionary_coin['date'] = date
                dictionary['Binance'] = temp
                dictionary_coin['Binance'] = temp_2
                date_bool = True
            else:
                dictionary = dictionary

            if coin == 'BTC':
                token = 'XBTUSD'
            else:
                token = coin + 'USD'
            #bitmex_query = f"select openInterest,symbol from bitmex_instrument where time >= now() - {time_period} and symbol =~ /{token}/"
            bitmex_query = f"select usd_denominated_open_interest,coin_denominated_open_interest,contract_symbol from exchange_open_interest where time >= now() - {time_period} and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(bitmex_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if(len(data) != 0):
                df = df.fillna(method='bfill')
                temp = []
                for key in data['time']:
                    t = data['time'][key][0:15]
                    t += "0"
                    if token in done and done[token] == t:
                        continue
                    else:
                        done[token] = t
                    if(data['usd_denominated_open_interest'][key] == 0 or data['coin_denominated_open_interest'][key] == 0):
                        continue
                    temp.append((int(data['usd_denominated_open_interest'][key])))
                    temp_2.append((int(data['coin_denominated_open_interest'][key])))
                    if data['usd_denominated_open_interest'][key] > max_value:
                        max_value = data['usd_denominated_open_interest'][key]
                    if data['usd_denominated_open_interest'][key] < min_value:
                        min_value = data['usd_denominated_open_interest'][key]
                    
                    if data['coin_denominated_open_interest'][key] > max_coin:
                        max_coin = data['coin_denominated_open_interest'][key]
                    if data['coin_denominated_open_interest'][key] < min_coin:
                        min_coin = data['coin_denominated_open_interest'][key]
                    date.append(t)
                if not (date_bool):
                    dictionary['date'] = date
                    date_bool = True
                dictionary['Bitmex'] = temp
                dictionary_coin['Bitmex'] = temp_2
            else:
                dictionary = dictionary

            token = coin + "-PERP"
            ftx_query = f"select usd_denominated_open_interest,coin_denominated_open_interest,contract_symbol from exchange_open_interest where time >= now() - {time_period} and contract_exchange  =~ /FTX/ and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(ftx_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if(len(data) != 0):
                df = df.fillna(method='bfill')
                temp = []
                for key in data['time']:
                    t = data['time'][key][0:15]
                    t += "0"
                    if token in done and done[token] == t:
                        continue
                    else:
                        done[token] = t
                    if(data['usd_denominated_open_interest'][key] == 0 or data['coin_denominated_open_interest'][key] == 0):
                        continue
                    temp.append((int(data['usd_denominated_open_interest'][key])))
                    temp_2.append((int(data['coin_denominated_open_interest'][key])))
                    if data['usd_denominated_open_interest'][key] > max_value:
                        max_value = data['usd_denominated_open_interest'][key]
                    if data['usd_denominated_open_interest'][key] < min_value:
                        min_value = data['usd_denominated_open_interest'][key]
                    
                    if data['coin_denominated_open_interest'][key] > max_coin:
                        max_coin = data['coin_denominated_open_interest'][key]
                    if data['coin_denominated_open_interest'][key] < min_coin:
                        min_coin = data['coin_denominated_open_interest'][key]
                    date.append(t)
                if not (date_bool):
                    dictionary['date'] = date
                    date_bool = True
                    print(date_bool)
                dictionary['Ftx'] = temp
                dictionary_coin['Ftx'] = temp_2
            else:
                dictionary = dictionary
            


            """
            token = coin + "USD"
            bybit_query =  f"select open_interest,symbol from bybit_tickers where time >= now() - {time_period} and symbol =~ /{token}/"
            df = pd.DataFrame(client.query(bybit_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if(len(data) != 0):
                df = df.fillna(method='bfill')
                temp = []
                for key in data['time']:
                    t = data['time'][key][0:15]
                    t += "0"
                    if token in done and done[token] == t:
                        continue
                    else:
                        done[token] = t
                    if(data['open_interest'][key] == 0):
                        continue
                    temp.append(str(int(data['open_interest'][key])))
                    if data['open_interest'][key] > max_value:
                        max_value = data['open_interest'][key]
                    if data['open_interest'][key] < min_value:
                        min_value = data['open_interest'][key]
                    date.append(t)
                dictionary['Bybit'] = temp
            else:
            """

            token = coin + "-USD"
            huobi_query =  f"select usd_denominated_open_interest,coin_denominated_open_interest,contract_symbol from exchange_open_interest where time>= now() - {time_period}  and contract_exchange =~ /Huobi/ and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(huobi_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if(len(data) != 0):
                df = df.fillna(method='bfill')
                temp = []
                for key in data['time']:
                    t = data['time'][key][0:15]
                    t += "0"
                    if token in done and done[token] == t:
                        continue
                    else:
                        done[token] = t
                    if(data['usd_denominated_open_interest'][key] == 0 or data['coin_denominated_open_interest'][key] == 0):
                        continue
                    temp.append((int(data['usd_denominated_open_interest'][key])))
                    temp_2.append((int(data['coin_denominated_open_interest'][key])))
                    if data['usd_denominated_open_interest'][key] > max_value:
                        max_value = data['usd_denominated_open_interest'][key]
                    if data['usd_denominated_open_interest'][key] < min_value:
                        min_value = data['usd_denominated_open_interest'][key]
                    
                    if data['coin_denominated_open_interest'][key] > max_coin:
                        max_coin = data['coin_denominated_open_interest'][key]
                    if data['coin_denominated_open_interest'][key] < min_coin:
                        min_coin = data['coin_denominated_open_interest'][key]
                    date.append(t)
                if not (date_bool):
                    print(date_bool)
                    dictionary['date'] = date
                    date_bool = True
                dictionary['Huobi'] = temp
                dictionary_coin['Huobi'] = temp_2
            else:
                dictionary = dictionary

            token = coin + "-USD-SWAP"
            okex_query =  f"select usd_denominated_open_interest,coin_denominated_open_interest,contract_symbol from exchange_open_interest where time>= now() - {time_period}  and contract_exchange =~ /Okex/ and contract_symbol =~ /{token}/"
            df = pd.DataFrame(client.query(okex_query, chunked=True, chunk_size=10000).get_points())
            data = df.to_dict()
            if(len(data) != 0):
                df = df.fillna(method='bfill')
                temp = []
                for key in data['time']:
                    t = data['time'][key][0:15]
                    t += "0"
                    if token in done and done[token] == t:
                        continue
                    else:
                        done[token] = t
                    if(data['usd_denominated_open_interest'][key] == 0 or data['coin_denominated_open_interest'][key] == 0):
                        continue
                    temp.append((int(data['usd_denominated_open_interest'][key])))
                    temp_2.append((int(data['coin_denominated_open_interest'][key])))
                    if data['usd_denominated_open_interest'][key] > max_value:
                        max_value = data['usd_denominated_open_interest'][key]
                    if data['usd_denominated_open_interest'][key] < min_value:
                        min_value = data['usd_denominated_open_interest'][key]
                    
                    if data['coin_denominated_open_interest'][key] > max_coin:
                        max_coin = data['coin_denominated_open_interest'][key]
                    if data['coin_denominated_open_interest'][key] < min_coin:
                        min_coin = data['coin_denominated_open_interest'][key]
                    date.append(t)
                if  not (date_bool):
                    dictionary['date'] = date
                    date_bool = True
                dictionary['Okex'] = temp
                dictionary_coin['Okex'] = temp_2
            else:
                dictionary = dictionary

            with open(path + coin + '-' + time_period + '-open-interest-usd.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(dictionary.keys())
                writer.writerows(zip(*dictionary.values()))
            with open(path + coin + '-' + time_period + '-open-interest-coin.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(dictionary_coin.keys())
                writer.writerows(zip(*dictionary_coin.values()))
            print(coin)
            print(max_value,min_value)
            print(max_coin,min_coin)



def find_all():
    find_liquidation_bitmex()
    print("bitmex - liquidation")
    find_liquidation_binance()
    print("binance - liquidation")
    find_liquidation_okex()
    print("okex - liquidation")
    find_liquidation_ftx()
    print("ftx - liquidation")
    find_price()
    print("prices")
    make_table()
    print("tables")
    find_open_interest()

    
if __name__ == '__main__':
    open_interest_price_btc()
    #coin_open_interest()
    #open_interest_price_btc()
    #deribit()
    #bitmex()
    #btc_eth_open_interest(['XBTUSD','ETHUSD'])
 
    

