import ccxt
from dotenv import load_dotenv
import os
import time

from pybit.unified_trading import HTTP

load_dotenv()

bybit = ccxt.bybit({
    'apiKey': os.getenv('BYBIT_API_KEY'),
    'secret':  os.getenv('BYBIT_API_SECRET'),
})

hyperliquid = ccxt.hyperliquid({
    'walletAddress': os.getenv('HYPERLIQUID_WALLET'),
    'privateKey':  os.getenv('HYPERLIQUID_SECRET_KEY'),
})

# balance = hyperliquid.fetch_balance()
# print(balance)
# print(hyperliquid.load_markets())

# o = hyperliquid.create_order('ETH/USDC:USDC', 'limit', 'buy', 0.01, 3550)
# print(o)

# b = bybit.fetch_balance()
# print(b)

# order = bybit.create_order('ETH/USDT:USDT', 'limit', 'buy', 0.01, 3480)
# print(order)

# book = hyperliquid.fetch_order_book('ETH/USDC:USDC')
# print(book)
# print(book['bids'][1][0])
# hyperliquid.fetch_order_status


def leg_bybit(exchange, pair, qty, direction):
    book = exchange.fetch_order_book(pair)
    price = book['bids' if direction=='buy' else 'asks'][2][0]
    # price = 3550
    order = exchange.create_order(pair, 'limit', 'buy', qty, price)
    print(f"BL - open {direction} leg: {order['id']}")

    while True:
        last_order = exchange.fetchOpenOrder(order['id'])
        if last_order['status'] == 'closed':
            print('BL: Order filled.')
            break
        elif last_order['status'] == 'canceled':
            print('BL: Order canceled.')
            break
        else:
            print('BL: Order not filled yet. Checking again in 5 sec...')
            time.sleep(5)

def leg_hyper(exchange, pair, qty, direction):
    book = exchange.fetch_order_book(pair)
    price = book['bids' if direction=='buy' else 'asks'][1][0]
    # price = 3550
    order = exchange.create_order(pair, 'limit', direction, qty, price)
    print(f"HL - open {direction} leg: {order['id']}")

    while True:
        last_order = exchange.fetch_order(order['id'])
        if last_order['status'] == 'closed':
            print('HL: Order filled.')
            break
        elif last_order['status'] == 'canceled':
            print('HL: Order canceled.')
            break
        else:
            print('HL: Order not filled yet. Checking again in 5 sec...')
            time.sleep(5)

# leg_hyper(hyperliquid, 'ETH/USDC:USDC', 0.01, 'buy')

# leg_bybit(bybit, 'ETH/USDT:USDT', 0.01, 'buy')

def open_trade(hyper, bybit, amount, asset, wl=1, tranche=4):
    if wl not in [1, 2]:
        raise ValueError("The parameter 'wl' must be either 1 or 2.")
    amount_tranche = amount / tranche
    pair_USDC = f'{asset}/USDC:USDC'
    pair_USDT = f'{asset}/USDT:USDT'
    ticker = bybit.fetch_ticker(pair_USDT)
    qty = round((amount_tranche / ticker['last']) * 0.95, 0) # add automatic formatting
    print(f"{asset} qty: {qty}")

    i = 1
    while i <= tranche:
        print(f"Tranche n. {i} starting:")
        leg_hyper(hyper, pair_USDC, qty, 'buy' if wl==1 else 'sell')
        leg_bybit(bybit, pair_USDT, qty, 'buy' if wl==2 else 'sell')
        print(f"Tranche n. {i} done.")
        i += 1


# qty = bybit.fetch_ticker('ETH/USDT:USDT')
# print(qty['last'])

# open_trade(hyperliquid, bybit, 300, 'PENGU', wl=2, tranche=2)

def check_fr(hyperliquid, bybit, asset):
    '''
    Check the difference between the funding rates of two exchanges.

    Delta positive when bybit rate > hyperliquid rate.

    IF delta positive --> short bybit, long hyperliquid
    '''
    fr_bybit = bybit.fetch_funding_rate(f'{asset}/USDT:USDT')
    fr_hyper = hyperliquid.fetch_funding_rate(f'{asset}/USDC:USDC')

    fr_delta = float(fr_bybit['fundingRate']) - float(fr_hyper['fundingRate']*8) # add automatic formatting for interval

    return fr_delta


def quantity(asset, qty):
    ticker = hyperliquid.fetch_ticker(f'{asset}/USDC:USDC')
    true_qty = round((qty / ticker['last']) * 0.95, 0) # add automatic formatting
    
    return ticker

    # func to round down the quantity to the nearest decimal depending on the asset

# print(quantity('PENGU', 300))

def check_open_trade(exchange, pair):
    trade = exchange.fetch_open_orders(pair)

    print(trade)


def get_open_trades(exchange):
    trades = exchange.fetch_positions()
    open_positions = {}
    for trade in trades:
        symbol = trade['symbol']
        size = trade['contracts']
        side = trade['side']
        open_positions[symbol] = size, side

    return open_positions


order = hyperliquid.create_order('ETH/USDC:USDC', 'limit', 'buy', 0.05, 3300)
last_order = hyperliquid.fetchOpenOrder(order['id'])
print(last_order['status'])

