import time
import logging
import os
from src.exchanges import initialize_exchanges
from src.strategies import simple_strategy

if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(filename='logs/bot.log', level=logging.INFO)

def run_bot():
    bybit, hyperliquid = initialize_exchanges()

    while True:
        try:
            simple_strategy(hyperliquid)
            time.sleep(60)  # Run every minute
        except Exception as e:
            logging.error(f"Error running bot: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_bot()