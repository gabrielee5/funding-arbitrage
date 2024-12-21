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

def leg_bybit(exchange, pair, qty, direction):
    book = exchange.fetch_order_book(pair)
    price = book['bids' if direction=='buy' else 'asks'][2][0]
    exchange = 'bybit'
    order = exchange.create_order(pair, 'limit', direction, qty, price)
    print(f"{exchange} - open {direction} leg: {order['id']}")

    while True:
        last_order = exchange.fetchOpenOrder(order['id'])
        if last_order['status'] == 'closed':
            print(f'{exchange} Order filled.')
            break
        elif last_order['status'] == 'canceled':
            print(f'{exchange} Order canceled.')
            break
        else:
            print(f'{exchange} Order not filled yet. Checking again in 5 sec...')
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



# controllare se questa versione si puo usare per entrambi
def place_leg_order(exchange, pair, qty, direction, exchange_name):
    book = exchange.fetch_order_book(pair)
    # Different price index based on exchange
    price_index = 2 if exchange_name == 'bybit' else 1
    price = book['bids' if direction=='buy' else 'asks'][price_index][0]
    
    order = exchange.create_order(pair, 'limit', direction, qty, price)
    exchange_display = 'bybit' if exchange_name == 'bybit' else 'HL'
    print(f"{exchange_display} - open {direction} leg: {order['id']}")

    while True:
        # Handle different fetch order methods
        last_order = (exchange.fetchOpenOrder(order['id']) 
                     if exchange_name == 'bybit' 
                     else exchange.fetch_order(order['id']))
        
        if last_order['status'] == 'closed':
            print(f'{exchange_display}: Order filled.')
            break
        elif last_order['status'] == 'canceled':
            print(f'{exchange_display}: Order canceled.')
            break
        else:
            print(f'{exchange_display}: Order not filled yet. Checking again in 5 sec...')
            time.sleep(5)



def open_trade(hyperliquid, bybit, amount, asset, tranche=2):
    
    fr_delta = check_fr(hyperliquid, bybit, asset)
    if fr_delta > 0:
        short_hyper = False
        short_bybit = True
        print('FR bybit > FR hyperliquid --> Short bybit, long hyperliquid.')
    else:
        short_hyper = True
        short_bybit = False
        print('FR hyperliquid > FR bybit --> Short hyperliquid, long bybit.')

    amount_tranche = amount / tranche
    pair_USDC = f'{asset}/USDC:USDC'
    pair_USDT = f'{asset}/USDT:USDT'
    ticker = bybit.fetch_ticker(pair_USDT)
    qty = round(amount_tranche / ticker['last'], 0) # add automatic formatting
    print(f"{asset} qty: {qty}")

    i = 1
    while i <= tranche:
        print(f"Tranche n. {i} starting:")
        leg_hyper(hyperliquid, pair_USDC, qty, 'sell' if short_hyper else 'buy')
        leg_bybit(bybit, pair_USDT, qty, 'sell' if short_bybit else 'buy')
        print(f"Tranche n. {i} done.")
        i += 1

    print('Trade completed.')

def get_open_trades(exchange):
    trades = exchange.fetch_positions()
    open_positions = {}
    for trade in trades:
        symbol = trade['symbol']
        size = trade['contracts']
        side = trade['side']
        open_positions[symbol] = size, side

    return open_positions

def exit_trade(hyperliquid, bybit, asset, tranche=1):
    bybit_positions = get_open_trades(bybit)
    hyper_positions = get_open_trades(hyperliquid)
    
    pair_USDC = f'{asset}/USDC:USDC'
    pair_USDT = f'{asset}/USDT:USDT'

    qty_hyper = hyper_positions[pair_USDC][0]
    qty_bybit = bybit_positions[pair_USDT][0]

    if hyper_positions[pair_USDC][1] == 'long' and bybit_positions[pair_USDT][1] == 'short':
        short_hyper = True
        short_bybit = False
    elif hyper_positions[pair_USDC][1] == 'short' and bybit_positions[pair_USDT][1] == 'long':
        short_hyper = False
        short_bybit = True
    else:
        print("This should not happen.")
        return

    i = 1
    while i <= tranche:
        print(f"Tranche n. {i} starting:")
        leg_hyper(hyperliquid, pair_USDC, qty_hyper, 'sell' if short_hyper else 'buy')
        leg_bybit(bybit, pair_USDT, qty_bybit, 'sell' if short_bybit else 'buy')
        print(f"Tranche n. {i} done.")
        i += 1

if __name__ == '__main__':

    open_trade(hyperliquid, bybit, 300, 'BADGER', tranche=2)
    # exit_trade(hyperliquid, bybit, 'PENGU')

# creare una funcione simile anche per l'uscita. dividere in tranche e fare il rounding down della qty.
# nell'ultima tranche mettere tutta la qty rimasta.

