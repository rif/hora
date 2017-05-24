from pydash import py_
from gluon import current

class strategy(object):
    def __init__(self, min_period):
        self.min_period = min_period

    def create_offer(self, service, wallet):
        current.logger.debug("in strategy: {service}".format(service=service))
        bids = service.lend_bids(wallet['currency'])
        asks = service.lend_asks(wallet['currency'])

        # force min period for now
        # TODO: optimize this period
        min_lend_time = lambda l: l.period == self.min_period
        #highest_bid = bids[0] #current market dynamics allows this, but it's not a permanent thing
        highest_bid = py_.find(bids, min_lend_time) or bids[0]
        lowest_ask = py_.find(asks, min_lend_time)
        # make offer 5% under best ask
        offer_rate = self.determine_rate(highest_bid, lowest_ask)
        # place new offer
        current.logger.debug('  highest_bid:{0} lowest_ask:{1} will_offer:{2}'.format(highest_bid.rate, lowest_ask.rate, offer_rate))
        return service.new_offer(wallet['currency'], wallet['available'], offer_rate, lowest_ask.period)

    def determine_rate(self, highest_bid, lowest_ask):
        raise NotImplementedError


class BelowBestAskStrategy(strategy):
    def __init__(self, min_period=2, percent=0.95):
        super(self.__class__, self).__init__(min_period)
        self.percent = percent

    def determine_rate(self, highest_bid, lowest_ask):
        rate = float(highest_bid.rate) + self.percent * (float(lowest_ask.rate) - float(highest_bid.rate))
        return max(highest_bid.rate, rate)



class BestBidStrategy(strategy):
    def __init__(self, min_period=2):
        super(self.__class__, self).__init__(min_period)

    def determine_rate(self, highest_bid, lowest_ask):
        return float(highest_bid.rate)

class SmartStrategy(strategy):
    def __init__(self, min_period=2):
        super(self.__class__, self).__init__(min_period)

    def determine_rate(self, highest_bid, lowest_ask):
        return float(highest_bid.rate)
