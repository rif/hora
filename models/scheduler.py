from gluon.scheduler import Scheduler
from provider_clients import clients
from gluon import current
from pydash import py_

db_task = DAL(myconf.get('db_task.uri'), migrate_enabled=myconf.get('db_task.migrate'))

def task_reinvest():
    current.logger.debug('Starting reinvest task...')
    
    providers = db(db.provider.status=='enabled').select()
    offers_made = []
    for provider in providers:
        service = clients[provider.service](provider.api_key, provider.secret)
        wallets = service.wallets()
        for wallet in wallets:
            # TODO: "deposit" type is bitfinex terminology. do better job of standardizing wallet output
            if 'type' in wallet and wallet['type']=='deposit':
                minOffer = service.min_lend(wallet['currency'])
                current.logger.debug('  {0} ({1}): {2} {3} available to lend. Min lend is {4}'.format(provider.service, provider.name, float(wallet['available']), wallet['currency'], minOffer))
                if float(wallet['available']) > minOffer:

                    # TODO: move this into a strategy
                    bids = service.lend_bids(wallet['currency'])
                    asks = service.lend_asks(wallet['currency'])
                    
                    # force min period for now
                    min_lend_time = lambda l: l.period == 2
                    # highest_bid = bids[0] #current market dynamics allows this, but it's not a permanent thing
                    highest_bid = py_.find(bids, min_lend_time)
                    lowest_ask = py_.find(asks, min_lend_time)
                    # make offer 5% under best ask
                    offer_rate = float(highest_bid.rate) + 0.95 * (float(lowest_ask.rate) - float(highest_bid.rate))
                    # place new offer
                    current.logger.debug('  highest_bid:{0} lowest_ask:{1} will_offer:{2}'.format(highest_bid.rate, lowest_ask.rate, offer_rate))
                    offers_made.append(service.new_offer(wallet['currency'], wallet['available'], offer_rate, lowest_ask.period))

                    # TODO: create transaction history item for reporting
    return offers_made


scheduler = Scheduler(db_task, tasks={
    'reinvest': task_reinvest,
})
