def simple_strategy(exchange):
    # Example strategy: fetch balance and print it
    balance = exchange.fetch_balance()
    print(balance)

def open_legs(exchange_long, exchange_short, qty, asset):
    pair = f'{asset}/USD'
    leg_long = exchange_long.create_limit()


def enter_tight_limit(exchange, qty, asset, price):
    pair = f'{asset}/USDT:USDT'

    order = exchange.create_order(pair, 'limit', 'buy', 0.01, 3480)

def long_leg(exchange, qty, asset, price):
    pair = f'{asset}/USDT:USDT'
    book = exchange.fetch_order_book(pair)
    order = exchange.create_order(pair, 'limit', 'buy', qty, book['bids'][5][0])
