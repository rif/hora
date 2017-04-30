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
                current.logger.debug('  {0}: {1} {2} available to lend. Min lend is {3}'.format(provider.service, float(wallet['available']), wallet['currency'], minOffer))
                if float(wallet['available']) > minOffer:
                    # TODO: revamp all this
                    bids = service.lend_bids(wallet['currency'])
                    asks = service.lend_asks(wallet['currency'])
                    
                    # force min period for now
                    min_lend_time = lambda l: l.period == 2
                    best_bid = bids[0] #current market dynamics allows this, but it's not a permanent thing
                    best_ask = py_.find(asks, min_lend_time)
                    # make offer 15% under best ask
                    offer_rate = float(best_bid.rate) + 0.85 * (float(best_ask.rate) - float(best_bid.rate))
                    
                    # place new offer
                    current.logger.debug('  best_bid:{0} best_ask:{1} will_offer:{2}'.format(best_bid.rate, best_ask.rate, offer_rate))
                    offers_made.append(service.new_offer(wallet['currency'], wallet['available'], offer_rate, best_ask.period))
                    # TODO: create transaction history item for reporting
    return offers_made


scheduler = Scheduler(db_task, tasks={
    'reinvest': task_reinvest,
})
