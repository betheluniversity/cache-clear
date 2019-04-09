from flask import Flask
from bu_cascade.cascade_connector import Cascade

app = Flask(__name__)
app.config.from_object('config')
app.url_map.strict_slashes = False

cascade_connector = Cascade(app.config['SOAP_URL'], app.config['CASCADE_LOGIN'], app.config['SITE_ID'], app.config['STAGING_DESTINATION_ID'])

from app.views.views import HomeView
HomeView.register(app, route_base='/')

from app.views.rpapi import RefreshPurgeView
RefreshPurgeView.register(app, route_base='/rpapi')
