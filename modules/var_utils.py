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
