def compact_lends_book(lends):
    new_lends = []
    current_rate = float(lends[0]['rate'])
    current_amount = float(lends[0]['amount'])
    current_period = lends[0]['period']
    for lend in lends[1:]:
        if current_period == lend['period'] and current_rate > 0.001 and current_rate - float(lend['rate']) < 0.01:
            current_amount += float(lend['amount'])
        else:
            new_lends.append({'rate':current_rate, 'amount':current_amount, 'period':current_period})
            current_amount = float(lend['amount'])
            current_rate = float(lend['rate'])
            current_period = lend['period']
    return new_lends

def to_pretty_currency(amount, currency):
    currency = currency.upper()
    if currency == 'USD':
        return '{:,.2f}'.format(amount)
    elif currency == 'BTC':
        return '{:,.6f}'.format(amount)
    else:
        return '{:,.3f}'.format(amount)


def prettify_lends_book(lends, currency):
    pretty_lends = []
    for lend in lends:
        rate = lend['rate']
        if rate > 0.001:
            rate = '{:,.3f} %'.format(float(lend['rate']))
        pretty_lends.append({'period':lend['period'], 'amount':to_pretty_currency(lend['amount'], currency), 'rate':rate })
    return pretty_lends

def daily_to_apr(rate):
    """Converts a daily interest rate to an annual percentage rate.

    rate - the daily periodic rate
    See http://www.investopedia.com/terms/a/apr.asp Section: "APR vs Daily Periodic Rate"
    returns the rate*365*100
    """
    return (rate * 365 * 100)
