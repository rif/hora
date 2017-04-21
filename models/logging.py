import logging

#based on http://www.web2py.com/books/default/chapter/29/04/the-core#Logging
#be sure to set app.name in appconfig.ini, and add corresponding entry in logging.conf

logger = logging.getLogger("web2py.app." + AppConfig().get('app.name'))
logger.setLevel(logging.DEBUG)
