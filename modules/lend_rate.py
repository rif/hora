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

#    def to_dict(self):
#        lb_dict = self._asdict()
#        lb_dict['apr'] = self.apr
#        lb_dict['daily_rate'] = self.daily_rate
#        lb_dict['rate_of_return'] = self.rate_of_return
#        return lb_dict

    #note, maybe this approach is a bit too clever, and should just be the above
    # https://stackoverflow.com/questions/11637293/iterate-over-object-attributes-in-python
    def to_dict(self):
        lb_dict = {}
        for a in dir(self):
            if not a.startswith('_') and not callable(getattr(self,a)):
                lb_dict[a] = getattr(self, a)
        return lb_dict