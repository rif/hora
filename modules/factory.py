from bitfinex import Bitfinex
from poloniex import Poloniex
from strategies import BelowBestAskStrategy, BestBidStrategy

clients = {
    "Bitfinex": Bitfinex,
    "Poloniex": Poloniex
}

strategies = {
    'Below_Best_Ask': BelowBestAskStrategy,
    'Best_Bid': BestBidStrategy,
}
