from flask import Flask

app = Flask(__name__)
app.config.from_object('config')
app.url_map.strict_slashes = False

from app.views.base import HomeView
HomeView.register(app, route_base='/')

from app.views.thumbor import ThumborView
ThumborView.register(app, route_base='/thumbor')

from app.views.rpapi import RefreshPurgeView
RefreshPurgeView.register(app, route_base='/rpapi')
