# Imports from Python global packages
import re

# Imports from packages installed from requirements.txt
from flask import render_template, request
from flask_classy import FlaskView, route

# Imports from elsewhere in this project
from app.forms.rpapi import PurgeRefreshForm, SimpleBanForm, AdvancedBanForm
from app.controllers.rpapi import rpapi_call


class RefreshPurgeView(FlaskView):

    def index(self):
        prform = PurgeRefreshForm()
        sbform = SimpleBanForm()
        abform = AdvancedBanForm()
        return render_template('rpapi.html', **locals())

    @route('/purge-refresh-submit', methods=['POST'])
    def purge_refresh_submit(self):
        prform = PurgeRefreshForm(request.form)
        is_valid = prform.validate()
        if not is_valid:
            sbform = SimpleBanForm()
            abform = AdvancedBanForm()
            return render_template('rpapi.html', **locals())

        host_url_groups = re.compile(r'(https?://)?([^/]+)(/.*)').search(prform.get('uri'))
        host = host_url_groups.group(2)
        url = host_url_groups.group(3)

        rpapi_result = rpapi_call(action=prform.get('api_action'), host=host, url=url)
        return render_template('rpapi_response.html', api_response=rpapi_result)

    @route('/simple-ban-submit', methods=['POST'])
    def simple_ban_submit(self):
        sbform = SimpleBanForm(request.form)
        is_valid = sbform.validate()
        if not is_valid:
            prform = PurgeRefreshForm()
            abform = AdvancedBanForm()
            return render_template('rpapi.html', **locals())

        rpapi_result = rpapi_call(action='simple_ban', host=sbform.get('host'), url=sbform.get('url'))
        return render_template('rpapi_response.html', api_response=rpapi_result)

    @route('/advanced-ban-submit', methods=['POST'])
    def advanced_ban_submit(self):
        abform = AdvancedBanForm(request.form)
        is_valid = abform.validate()
        if not is_valid:
            prform = PurgeRefreshForm()
            sbform = SimpleBanForm()
            return render_template('rpapi.html', **locals())

        rpapi_result = rpapi_call(action='advanced_ban', advanced_ban_expression=abform.get('expression'))
        return render_template('rpapi_response.html', api_response=rpapi_result)
