from gluon.scheduler import Scheduler
from provider_clients import clients

db_task = DAL(myconf.get('db_task.uri'), migrate_enabled=myconf.get('db_task.migrate'))

def task_reinvest():
    providers = db(db.provider.status=='enabled').select()
    offers_made = []
    for provider in providers:
        service = clients[provider.service](provider.api_key, provider.secret)
        wallets = service.wallets()
        for wallet in wallets:
            # TODO: check for minimum lend offer
            if 'type' in wallet and wallet['type']=='deposit' and float(wallet['available']) > 0:
                # get best bid
                best_bid = service.lend_book('usd')['bids'][0]
                # place new offer
                offers_made.append(service.new_offer(wallet['currency'], wallet['available'], best_bid['rate'], best_bid['period']))
                # TODO: create transaction history item for reporting
    return offers_made


scheduler = Scheduler(db_task, tasks={
    'reinvest': task_reinvest,
})
