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
            # TODO: make this use real current rates!
            minOffer = 50
            if wallet['currency'].lower() == 'btc':
                minOffer = 0.043
            if wallet['currency'].lower() == 'eth':
                minOffer = 1.15
            if 'type' in wallet and wallet['type']=='deposit' and float(wallet['available']) > minOffer:
                # get best bid
                # TODO: don't rely on implicit ordering for best bid
                best_bid = service.lend_demand(wallet['currency'])[0]
                # place new offer
                offers_made.append(service.new_offer(wallet['currency'], wallet['available'], best_bid['rate'], best_bid['period']))
                # TODO: create transaction history item for reporting
    return offers_made


scheduler = Scheduler(db_task, tasks={
    'reinvest': task_reinvest,
})
