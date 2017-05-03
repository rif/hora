from bitfinex import Bitfinex
from poloniex import Poloniex
from strategies import BelowBestAskStrategy, BestBidStrategy

clients = {
    "Bitfinex": Bitfinex,
    "Poloniex": Poloniex
}

strategies = {
    'Below_Best_Ask': BelowBestAskStrategy(min_period=2, percent=0.95),
    'Best_Bid': BestBidStrategy(min_period=2),
}
