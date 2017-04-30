from collections import namedtuple

class LendRate(namedtuple('LendRate', 'rate, amount, period, rate_type, fee')):
    """Provides a consistent view of a Bid or Offer to borrow/lend funds regardless of provider"""
    
    @property
    def apr(self):
        if self.rate_type == 'apr':
            return float(self.rate)
        elif self.rate_type == 'daily':
            return float(self.rate) * 365 * 100
        else:
            raise ValueError('Unrecognized rate_type: %r' % self.rate_type)

    @property
    def daily_rate(self):
        if self.rate_type == 'apr':
            return float(self.rate) / 36500
        elif self.rate_type == 'daily':
            return float(self.rate)
        else:
            raise ValueError('Unrecognized rate_type: %r' % self.rate_type)

    @property
    def rate_of_return(self):
        return (1.0 - float(self.fee)) * self.apr