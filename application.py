import plotly
import plotly.graph_objs as go

import pandas as pd
import numpy as np
from importlib import reload
import json
from flask import Flask, render_template, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, join_room, emit, send
import bot
import test

import time

application = Flask(__name__)
auth = HTTPBasicAuth()
socketio = SocketIO(application)

users = {
    "virgilqr": generate_password_hash("virgilqr")
}

prices = {}
open_interest = {}
comparisons = {}
liquidations = {}
count = 0

@socketio.on('refresh_price')
def refresh_price():
    global prices
    p = bot.find_price()

    if count > 0:
        for coin in p:
            if not p[coin]:
                p[coin]=prices[coin]
            else:
                for exchange in prices[coin]:
                    if not p[coin][exchange]:
                        p[coin][exchange] = prices[coin][exchange]

    prices = p

    emit('draw_price_graphs', {'prices': prices})


@socketio.on('refresh_oi')
def refresh_oi():
    global open_interest
    global comparisons
    print('refresh_oi')
    prices = bot.find_price()
    open_interest = bot.find_open_interest1()
    emit('draw_oi_graphs')

'''
@socketio.on('refresh_oi')
def refresh_oi():
    global open_interest
    global comparisons
    print('refresh_oi')
    prices = bot.find_price()
    open_interest = bot.find_open_interest()
    comparisons = bot.find_comparisons()
    emit('draw_oi_graphs', {'open_interest': open_interest, 'prices': prices, 'comparisons':comparisons})
'''

@socketio.on('refresh_liquidations')
def refresh_liquidations():
    global liquidations
    liquidations = bot.find_liquidation()
    emit('draw_liquidations_graphs', {'liquidations': liquidations})


@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

@application.route('/refresh_oi')
#@auth.login_required
def refresh_oi():
    while(True):
        bot.find_open_interest()
        print('oi - done')

@application.route('/refresh_prices')
#@auth.login_required
def refresh_prices():
    print('p')
    bot.find_price()
    bot.make_table()

@application.route('/refresh_all')
#@auth.login_required
def refresh_all():
    print('all')
    bot.find_all()

@application.route('/refresh_liquidations')
#@auth.login_required
def refresh_liquidations():
    print('liq')
    bot.find_liquidation1()
    return True

@application.route('/refresh_volume')
def refresh_volume():
    print('liq')
    bot.find_volume()
    return True

@application.route('/')
#@auth.login_required
def main():
    return render_template('d3bitmex.html')

@application.route('/prices')
#@auth.login_required
def prices():
    return render_template('prices.html',
                            prices = prices,
                            )

@application.route('/d3ftxliquidations')
#@auth.login_required
def ftx_liquidations():
    return render_template('d3_ftx_liquidations.html',
    )

@application.route('/d3bitmexliquidations')
#@auth.login_required
def bitmex_liquidations():
    return render_template('d3_bitmex_liquidations.html',
                            )

@application.route('/d3okexliquidations')
#@auth.login_required
def okex_liquidations():
    return render_template('d3_okex_liquidations.html',
                            )

@application.route('/d3binanceliquidations')
#@auth.login_required
def binance_liquidations():
    return render_template('d3_binance_liquidations.html',)

@socketio.on('refresh_price')
def refresh_price1():
    bot.find_price()
    emit('draw_price_graphs')

@application.route('/d3bitmexvolume')
#@auth.login_required
def bitmex_volume():
    return render_template('d3_bitmex_volume.html',
                            )
@application.route('/d3Prices')
#@auth.login_required
def prices1():
    return render_template('d3_prices.html',
                            )

@application.route('/d3Comparisons')
#@auth.login_required
def comparisons1():
    return render_template('d3_comparisons.html',
                            )

@application.route('/refresh_bitmex')
#@auth.login_required
def refresh_bitmex():
    bot.bitmex()
    bot.open_interest_price_okex()

@application.route('/refresh_deribit')
#@auth.login_required
def refresh_deribit():
    bot.deribit()
    print('deribit')

@application.route('/d3bitmex')
#@auth.login_required
def bitmex():
    return render_template('d3bitmex.html')


@application.route('/refresh_binance')
#@auth.login_required
def refresh_binance():
    bot.binance()
    print('binance')

@application.route('/d3binance')
#@auth.login_required
def binance():
    return render_template('d3binance.html')

@application.route('/refresh_bybit')
#@auth.login_required
def refresh_bybit():
    bot.bybit()

@application.route('/d3bybit')
#@auth.login_required
def bybit():
    return render_template('d3bybit.html')

@application.route('/d3deribit')
#@auth.login_required
def deribit():
    return render_template('d3deribit.html')

@application.route('/refresh_okex')
#@auth.login_required
def refresh_okex():
    bot.okex()
    bot.open_interest_price_okex()

@application.route('/d3okexUSDswap')
#@auth.login_required
def okexUSDswap():
    return render_template('d3okexUSDswap.html')

@application.route('/d3okexUSDTswap')
#@auth.login_required
def okexUSDTswap():
    return render_template('d3okexUSDTswap.html')

@application.route('/d3okexUSDfutures')
#@auth.login_required
def okexUSDfutures():
    return render_template('d3okexUSDfutures.html')

@application.route('/d3okexUSDTfutures')
#@auth.login_required
def d3okexUSDTfutures():
    return render_template('d3okexUSDTfutures.html')

@application.route('/refresh_ftx')
#@auth.login_required
def refresh_ftx():
    bot.ftx()

@application.route('/d3ftx')
#@auth.login_required
def ftx():
    return render_template('d3FTX.html')

@application.route('/refresh_huobi')
#@auth.login_required
def refresh_huobi():
    bot.huobi()

@application.route('/d3huobi')
#@auth.login_required
def huobi():
    return render_template('d3huobi.html')

@application.route('/d3btc-oi')
#@auth.login_required
def btc_oi():
    return render_template('d3btc-oi.html')

@application.route('/d3eth-oi')
#@auth.login_required
def eth_oi():
    return render_template('d3eth-oi.html')

@application.route('/d3xrp-oi')
#@auth.login_required
def xrp_oi():
    return render_template('d3xrp-oi.html')

@application.route('/d3bch-oi')
#@auth.login_required
def bch_oi():
    return render_template('d3bch-oi.html')

@application.route('/d3bsv-oi')
#@auth.login_required
def bsv_oi():
    return render_template('d3bsv-oi.html')

@application.route('/d3ltc-oi')
#@auth.login_required
def ltc_oi():
    return render_template('d3ltc-oi.html')

@application.route('/d3bnb-oi')
#@auth.login_required
def bnb_oi():
    return render_template('d3bnb-oi.html')

@application.route('/d3eos-oi')
#@auth.login_required
def eos_oi():
    return render_template('d3eos-oi.html')

@application.route('/d3trx-oi')
#@auth.login_required
def trx_oi():
    return render_template('d3trx-oi.html')

@application.route('/d3open-interest', methods=['GET', 'POST'])
#@auth.login_required
def d3openinterest():
    max_value = 0
    min_value = 0
    if request.method == 'POST':
        tokens = (request.form.getlist('token'))
        print(tokens)
        max_value,min_value = bot.btc_eth_open_interest(tokens)
        #bot.find_open_interest()
        #max_value,min_value = bot.stack_open_interest()
    else:
        return render_template('d3open-interest.html', max_value = max_value, min_value = min_value)
    return render_template('d3open-interest.html', max_value = max_value, min_value = min_value)

if __name__ == '__main__':
    #bot.find_all()
    #application.run()
    #bot.find_all()
    socketio.run(application)
    
    

