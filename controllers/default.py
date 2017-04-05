# -*- coding: utf-8 -*-
from prov import provider_classes

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

def lends():
    bf = provider_classes['Bitfinex']()
    lends =  bf.lends('USD')
    return dict(lends = lends)

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
