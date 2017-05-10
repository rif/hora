from gluon.scheduler import Scheduler
from factory import clients, strategies
from gluon import current

db_task = DAL(myconf.get('db_task.uri'), migrate_enabled=myconf.get('db_task.migrate'))

def task_check_wallets():
    current.logger.debug('Starting reinvest task...')

    providers = db(db.provider.status=='enabled').select()
    wallets_found = []
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
                                         pvars=dict(service=service, wallet=wallet, provider=provider),
                                         repeats=1,  # run 1 time
                                         timeout=600,  # should take less than 5 min
                                         retry_failed=-1, # retry for unlimited times (if failed)
                                         )
                    wallets_found.append(wallets)
    return wallets_found


def task_reinvest(service, wallet, provider):
    strategy = strategies[provider.strategy]

    lock_id = db.wallet_lock.insert(
        wallet_owner = provider.created_by,
        provider = provider.id,
    )
    db.offer.insert(
        wallet_lock=lock_id,
                    offer_id="x",
                    currency=wallet['currency'],
                    amount=wallet['available'],
                    rate=22.3,
                    period=4
                )
    #response = strategy.create_offer(wallet, service)

    # create offer history item for reporting
    #offer_id = ''
    #if 'offer_id' in response:
    #    offer_id = response['offer_id']
    #    if 'orderID' in response:
    #        offer_id = response['orderID']
    #        if offer_id:
    #            db.offer.insert(
    #                offer_id=offer_id,
    #                offered_by=provider.created_by,
    #                currency=wallet['currency'],
    #                amount=wallet['available'],
    #                rate=offer_rate,
    #                period=lowest_ask.period
    #            )
    db.commit()
    return response


scheduler = Scheduler(db_task, tasks={
    'check_wallets': task_check_wallets,
    'reinvest': task_reinvest,
})
