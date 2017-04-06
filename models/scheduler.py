from gluon.scheduler import Scheduler
from prov import provider_classes

def task_reinvest():
    print 'start'
    providers = db(db.provider.status=='enabled').select()
    for provider in providers:
        service = provider_classes[provider.service](provider.api_key, provider.secret)
        wallets = service.wallets()
        for wallet in wallets:
            print wallet


scheduler = Scheduler(db, tasks={
    'reinvest': task_reinvest,
})
