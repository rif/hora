def compact_lends_book(lends):
    new_lends = []
    current_rate = float(lends[0]['rate'])
    current_amount = float(lends[0]['amount'])
    current_period = lends[0]['period']
    for lend in lends[1:]:
        if current_period == lend['period'] and current_rate - float(lend['rate']) < 0.01:
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
    for lend in lends[1:]:
        rate = '{:,.3f} %'.format(lend['rate'])
        pretty_lends.append({'period':lend['period'], 'amount':to_pretty_currency(lend['amount'], currency), 'rate':rate })
    return pretty_lends
