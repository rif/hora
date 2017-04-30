import urllib
import urllib2
import json
import time
import hmac,hashlib
from lend_rate import LendRate
from gluon import current
from pydash import py_


def createTimeStamp(datestr, format="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(datestr, format))

class Poloniex:
    def __init__(self, APIKey=None, Secret=None):
        self.APIKey = APIKey
        self.Secret = Secret
        self._fee = 0.15
        self._rate_type = 'daily'
        self._min_lend_amount = 0.01
        self._min_lend_base = 'btc'

    def post_process(self, before):
        after = before

        # Add timestamps if there isnt one but is a datetime
        if('return' in after):
            if(isinstance(after['return'], list)):
                for x in xrange(0, len(after['return'])):
                    if(isinstance(after['return'][x], dict)):
                        if('datetime' in after['return'][x] and 'timestamp' not in after['return'][x]):
                            after['return'][x]['timestamp'] = float(createTimeStamp(after['return'][x]['datetime']))

        return after

    def api_query(self, command, req={}):

        if(command == "returnTicker" or command == "return24Volume"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command))
            return json.loads(ret.read())
        elif(command == "returnOrderBook"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command + '&currencyPair=' + str(req['currencyPair'])))
            return json.loads(ret.read())
        elif(command == "returnLoanOrders"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command + '&currency=' + str(req['currency'])))
            return json.loads(ret.read())
        elif(command == "returnMarketTradeHistory"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + "returnTradeHistory" + '&currencyPair=' + str(req['currencyPair'])))
            return json.loads(ret.read())
        else:
            req['command'] = command
            req['nonce'] = int(time.time()*1000)
            post_data = urllib.urlencode(req)

            sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
            headers = {
                'Sign': sign,
                'Key': self.APIKey
            }

            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/tradingApi', post_data, headers))
            jsonRet = json.loads(ret.read())
            return self.post_process(jsonRet)


    def returnTicker(self):
        return self.api_query("returnTicker")

    def return24Volume(self):
        return self.api_query("return24Volume")

    def returnOrderBook (self, currencyPair):
        return self.api_query("returnOrderBook", {'currencyPair': currencyPair})

    def returnMarketTradeHistory (self, currencyPair):
        return self.api_query("returnMarketTradeHistory", {'currencyPair': currencyPair})


    # Returns all of your balances.
    # Outputs:
    # {"BTC":"0.59098578","LTC":"3.31117268", ... }
    def returnBalances(self):
        return self.api_query('returnBalances')

    # Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_XCP"
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs:
    # orderNumber   The order number
    # type          sell or buy
    # rate          Price the order is selling or buying at
    # Amount        Quantity of order
    # total         Total value of order (price * quantity)
    def returnOpenOrders(self,currencyPair):
        return self.api_query('returnOpenOrders',{"currencyPair":currencyPair})


    # Returns your trade history for a given market, specified by the "currencyPair" POST parameter
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs:
    # date          Date in the form: "2014-02-19 03:44:59"
    # rate          Price the order is selling or buying at
    # amount        Quantity of order
    # total         Total value of order (price * quantity)
    # type          sell or buy
    def returnTradeHistory(self,currencyPair):
        return self.api_query('returnTradeHistory',{"currencyPair":currencyPair})

    # Places a buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is buying at
    # amount        Amount of coins to buy
    # Outputs:
    # orderNumber   The order number
    def buy(self,currencyPair,rate,amount):
        return self.api_query('buy',{"currencyPair":currencyPair,"rate":rate,"amount":amount})

    # Places a sell order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is selling at
    # amount        Amount of coins to sell
    # Outputs:
    # orderNumber   The order number
    def sell(self,currencyPair,rate,amount):
        return self.api_query('sell',{"currencyPair":currencyPair,"rate":rate,"amount":amount})

    # Cancels an order you have placed in a given market. Required POST parameters are "currencyPair" and "orderNumber".
    # Inputs:
    # currencyPair  The curreny pair
    # orderNumber   The order number to cancel
    # Outputs:
    # succes        1 or 0
    def cancel(self,currencyPair,orderNumber):
        return self.api_query('cancelOrder',{"currencyPair":currencyPair,"orderNumber":orderNumber})

    # Immediately places a withdrawal for a given currency, with no email confirmation. In order to use this method, the withdrawal privilege must be enabled for your API key. Required POST parameters are "currency", "amount", and "address". Sample output: {"response":"Withdrew 2398 NXT."}
    # Inputs:
    # currency      The currency to withdraw
    # amount        The amount of this coin to withdraw
    # address       The withdrawal address
    # Outputs:
    # response      Text containing message about the withdrawal
    def withdraw(self, currency, amount, address):
        return self.api_query('withdraw',{"currency":currency, "amount":amount, "address":address})

    def lend_demand(self, currency, bids_asks):
        current.logger.debug('Getting {0} lend demand on Poloniex...'.format(currency))
        lb_json = self.api_query('returnLoanOrders', {"currency":currency})[bids_asks]
        lend_bids = []
        for lbj in lb_json:
            lend_bids.append(LendRate(rate=lbj['rate'], amount=lbj['amount'], period=lbj['rangeMin'], rate_type=self._rate_type, fee=self._fee))

        return sorted(lend_bids, key=lambda lb: float(lb.rate), reverse=True)

    def lend_bids(self, currency):
        return self.lend_demand(currency, 'demands')
        
    def lend_asks(self, currency):
        return self.lend_demand(currency, 'offers')

    def lend_matches(self, currency):
        demands = self.api_query('returnLoanOrders', {"currency":currency})
        return demands.keys()

    def wallets(self):
        wallets = self.api_query('returnAvailableAccountBalances')
        new_wallets = []
        # TODO: "deposit" type is bitfinex terminology. do better job of standardizing wallet output
        lending = py_.get(wallets, 'lending', dict(btc=0))
        for currency, amount in lending.iteritems():
            new_wallets.append(dict(available=amount, currency=currency, amount=amount, type='deposit'))
        return new_wallets

    def offers(self):
        ofs_dict = self.api_query('returnOpenLoanOffers')
        if isinstance(ofs_dict, list):
            return ofs_dict
        new_offers = []
        for currency, ofs in ofs_dict.iteritems():
            for of in ofs:
                new_offers.append(dict(rate=of['rate'], remaining_amount = of['amount'], original_amount = of['amount'], executed_amount = of['amount'], timestamp=createTimeStamp(of['date']), period=of['duration'], currency=currency, status='ACTIVE', id=of['id']))
        return new_offers

    def new_offer(self, currency, amount, rate, period, direction='lend'):
        return self.api_query('createLoanOffer', {'currency':currency, 'amount':amount, 'lendingRate':rate, 'duration':period})

    def cancel_offer(self, id):
        return self.api_query('cancelLoanOffer', {'orderNumber':id})

    def credits(self):
        cds = self.api_query('returnActiveLoans')['provided']
        new_credits = []
        for c in cds:
            new_credits.append(dict(timestamp=createTimeStamp(c['date']), period=c['duration'], currency=c['currency'], amount=c['amount'], rate=c['rate'], status='ACTIVE'))
        return new_credits

    def min_lend(self, currency):
        """computes the minimum lendable amount for the specified currency on this platform"""
        if currency.lower() == self._min_lend_base:
            return self._min_lend_amount
        else:
            pair = self._min_lend_base.upper() + '_' + currency.upper()
            path = pair + '.last'
            ticker = self.returnTicker()
            exrate = py_.get(ticker, path)
            if exrate is None:
                raise Exception('Failed to get last price for pair {0}'.format(pair))
            return self._min_lend_amount / float(exrate)