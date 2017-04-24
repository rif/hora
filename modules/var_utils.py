from lend_bid import LendBid

def compact_lends_book(lends):
    new_lends = []
    current_rate = lends[0].apr
    current_amount = float(lends[0].amount)
    current_period = lends[0].period
    for lend in lends[1:]:
        if current_period == lend.period and current_rate > 0.001 and current_rate - float(lend.apr) < 0.01:
            current_amount += float(lend.amount)
        else:
            #note this relies on the fact that all LendBids in the list being compacted utilize the same rate_type and fee...
            new_lends.append(LendBid(rate=current_rate, amount=current_amount, period=current_period, rate_type=lend.rate_type, fee=lend.fee))
            current_amount = float(lend.amount)
            current_rate = lend.apr
            current_period = lend.period
    return new_lends

def to_pretty_currency(amount, currency):
    currency = currency.upper()
    if currency == 'USD':
        return '{:,.2f}'.format(amount)
    elif currency == 'BTC':
        return '{:,.6f}'.format(amount)
    else:
        return '{:,.3f}'.format(amount)

