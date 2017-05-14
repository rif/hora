from gluon.scheduler import Scheduler
from factory import clients, strategies
from gluon import current

db_task = DAL(myconf.get('db_task.uri'), migrate_enabled=myconf.get('db_task.migrate'),fake_migrate_all=False)

def task_check_wallets():
    current.logger.debug('Starting reinvest task...')

    providers = db(db.provider.status=='enabled').select()
    providers_found = [] # providers with available amount in wallets
    for provider in providers:
        service = clients[provider.service](provider.api_key, provider.secret)
        wallets = service.wallets()
        for wallet in wallets:
            # TODO: "deposit" type is bitfinex terminology. do better job of standardizing wallet output
            if 'type' in wallet and wallet['type']=='deposit':
                minOffer = service.min_lend(wallet['currency'])
                current.logger.debug('  {0} ({1}): {2} {3} available to lend. Min lend is {4}'.format(provider.service, provider.name, float(wallet['available']), wallet['currency'], minOffer))
                if float(wallet['available']) > minOffer:
                    scheduler.queue_task('reinvest',
                                         pvars=dict(provider=dict(
                                             id=provider.id,
                                             service=provider.service,
                                             key=provider.api_key,
                                             secret=provider.secret,
                                             strategy=provider.strategy,
                                             created_by=provider.created_by,
                                         )),
                                         repeats=1,  # run 1 time
                                         timeout=600,  # should take less than 5 min
                                         retry_failed=0, # retry for unlimited times (if failed)
                                         )
                    providers_found.append(provider)
                    break # the task will check all wallets, skip to next provider
    if len(providers_found)>0:
        db_task.commit()
    return providers_found


def task_reinvest(provider):
    service = clients[provider['service']](provider['key'], provider['secret'])
    strategy = strategies[provider['strategy']]

    lock_id = db.wallet_lock.insert(
        wallet_owner = provider['created_by'],
        provider = provider['id'],
    )
    wallets = service.wallets()
    for wallet in wallets:
        offer = strategy.create_offer(service, wallet)

        # create offer history item for reporting
        offer_id = ''
        if 'offer_id' in offer:
            offer_id = offer['offer_id']
            if 'orderID' in offer:
                offer_id = offer['orderID']
                if offer_id:
                    db.offer.insert(
                        wallet_lock=lock_id,
                        offer_id=offer_id,
                        currency=wallet['currency'],
                        amount=wallet['available'],
                        rate=offer_rate,
                        period=lowest_ask.period
                    )
    db.commit()
    return 'ok'


scheduler = Scheduler(db_task, tasks={
    'check_wallets': task_check_wallets,
    'reinvest': task_reinvest,
})
