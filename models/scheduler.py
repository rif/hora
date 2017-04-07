from gluon.scheduler import Scheduler
from prov import provider_classes

db_task = DAL(myconf.get('db_task.uri'), migrate_enabled=myconf.get('db_task.migrate'))

def task_reinvest():
    providers = db(db.provider.status=='enabled').select()
    for provider in providers:
        service = provider_classes[provider.service](provider.api_key, provider.secret)
        wallets = service.wallets()
        for wallet in wallets:
            if 'type' in wallet and wallet['type']=='deposit':
                print float(wallet['available']),wallet['currency']
    return 'yyy'


scheduler = Scheduler(db_task, tasks={
    'reinvest': task_reinvest,
})
