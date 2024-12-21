import ccxt
from config.config import Config

def initialize_exchanges():
    bybit = ccxt.bybit({
        'enableRateLimit': True,
        'apiKey': Config.BYBIT_API_KEY,
        'secret': Config.BYBIT_SECRET_KEY,
    })

    hyperliquid = ccxt.hyperliquid({
        'walletAddress': Config.HYPERLIQUID_WALLET,
        'privateKey': Config.HYPERLIQUID_SECRET_KEY,
    })

    return bybit, hyperliquid