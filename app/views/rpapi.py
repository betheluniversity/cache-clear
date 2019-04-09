import re

from flask import render_template, request
from flask_classy import FlaskView, route

from app.forms.rpapi import PurgeRefreshForm, SimpleBanForm, AdvancedBanForm
from app.controllers.rpapi import rpapi_call


class RefreshPurgeView(FlaskView):

    def index(self):
        return render_template('rpapi.html')

    @route('/purge-refresh')
    def purge_refresh_form(self):
        return render_template('forms/purge_refresh.html', prform=PurgeRefreshForm())

    @route('/purge-refresh-submit', methods=['POST'])
    def purge_refresh_submit(self):
        form = PurgeRefreshForm(request.form)
        is_valid = form.validate()
        if not is_valid:
            return render_template('forms/purge_refresh.html', prform=form)

        host_url_groups = re.compile(r'(https?://)?([^/]+)(/.*)').search(form.get('uri'))
        host = host_url_groups.group(2)
        url = host_url_groups.group(3)

        rpapi_result = rpapi_call(action=form.get('api_action'), host=host, url=url)
        return render_template('rpapi_response.html', api_response=rpapi_result)

    @route('/simple-ban')
    def simple_ban_form(self):
        return render_template('forms/simple_ban.html', sbform=SimpleBanForm())

    @route('/simple-ban-submit', methods=['POST'])
    def simple_ban_submit(self):
        form = SimpleBanForm(request.form)
        is_valid = form.validate()
        if not is_valid:
            return render_template('forms/simple_ban.html', sbform=form)

        rpapi_result = rpapi_call(action='simple_ban', host=form.get('host'), url=form.get('url'))
        return render_template('rpapi_response.html', api_response=rpapi_result)

    @route('/advanced-ban')
    def advanced_ban_form(self):
        return render_template('forms/advanced_ban.html', abform=AdvancedBanForm())

    @route('/advanced-ban-submit', methods=['POST'])
    def advanced_ban_submit(self):
        form = AdvancedBanForm(request.form)
        is_valid = form.validate()
        if not is_valid:
            return render_template('forms/advanced_ban.html', abform=form)

        rpapi_result = rpapi_call(action='advanced_ban', advanced_ban_expression=form.get('expression'))
        return render_template('rpapi_response.html', api_response=rpapi_result)
