# -*- coding: utf-8 -*-
from prov import provider_classes
import var_utils

def index():
    return dict()

@auth.requires_login()
def providers():
    providers = db(db.provider.status=='enabled').select()
    form = crud.update(db.provider, request.args(0), next=URL('default', 'providers'))
    return locals()

@auth.requires_signature()
def delete_provider():
    provider_id = request.args(0) or redirect('default','index')
    form = FORM.confirm('Are you sure?',{'Back':URL('providers')})
    if form.accepted:
        crud.delete(db.provider, provider_id, next=URL('default', 'providers'), message=T('provider deleted succesfully'))
    response.view = 'default/confirm.html'
    return dict(form=form, entity='provider')

@auth.requires_signature()
def wallets():
    providers = db(db.provider.status=='enabled').select()
    wallets = {}
    for provider in providers:
        service = provider_classes[provider.service](provider.api_key, provider.secret)
        wallets[provider.name] = service.wallets()
    return dict(wallets=wallets)


@cache.action(time_expire=5, cache_model=cache.ram, prefix='lends', quick='VLP') # vars, lang and public
def lends():
    currency = request.vars.currency
    bf = provider_classes['Bitfinex']()
    lends =  var_utils.compact_lends_book(bf.lends(currency)['bids'])
    lends = var_utils.prettify_lends_book(lends, currency)
    return dict(lends = lends)

@auth.requires_login()
def ensure_task():
    scheduled_task = scheduler.task_status(db_task.scheduler_task.task_name == 'reinvest', output=True)
    if not scheduled_task:
        return scheduler.queue_task('reinvest',
                                    repeats=0,  # run unlimited times
                                    period=300,  # every 5 min
                                    timeout=240,  # should take less than 4 min
                                    retry_failed=-1, # retry for unlimited times (if failed)
                     )
    return BEAUTIFY(scheduled_task)

@auth.requires_login()
def status():
    return dict(request=request, session=session, response=response)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
