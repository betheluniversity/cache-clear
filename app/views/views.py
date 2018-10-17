# Imports from Python global packages
import time

# Imports from packages installed from requirements.txt
from flask import make_response, redirect, render_template, request, session, abort
from flask_classy import FlaskView, route
from werkzeug.datastructures import ImmutableMultiDict

# Imports from elsewhere in this project
from app import app, cascade_connector
from app.controllers.controller import clear_image_cache


class HomeView(FlaskView):

    def before_request(self, name, **kwargs):
        # reset session if it has been more than 12 hours
        # this portion of code was brought in from Tinker
        seconds_in_12_hours = 60 * 60 * 12  # equates to 12 hours
        if 'session_time' in session.keys() and not app.config['DEVELOPMENT']:
            reset_session = time.time() - session['session_time'] >= seconds_in_12_hours
        else:
            reset_session = True

        # if not production, then clear our session variables on each call
        if reset_session:
            session.clear()
            session['session_time'] = time.time() + seconds_in_12_hours

        if 'username' not in session.keys():
            if app.config['DEVELOPMENT']:
                session['username'] = app.config['TEST_USERNAME']
            else:
                session['username'] = request.environ.get('REMOTE_USER')
        if 'user_cascade_groups' not in session.keys():
            self._load_user_cascade_groups()

        if 'Administrators' not in session['user_cascade_groups']:
            abort(403)

    def _load_user_cascade_groups(self):
        try:
            user_object = cascade_connector.read(session['username'], 'user')
            allowed_groups = str(user_object['asset']['user']['groups'])
            session['user_cascade_groups'] = allowed_groups.split(';')

        # we are using a general except to make sure we are catching 503's
        except:
            session['mybethel_admin'] = False
            session['mybethel_admin_support'] = False
            session['user_cascade_groups'] = []

    def index(self):
        return render_template('index.html')

    @route('/post', methods=['POST'])
    def post(self):
        form = request.form
        if isinstance(form, ImmutableMultiDict):
            form_data = form.to_dict()
        else:
            form_data = {}

        cleared_path = form_data['path']
        matches = clear_image_cache(cleared_path)

        return render_template('ajax_post.html', **locals())

    @route('/favicon.ico')
    def favicon(self):
        return redirect('/static/images/favicon.ico')

    def logout(self):
        session.clear()
        resp = make_response(redirect(app.config['LOGOUT_URL']))
        resp.set_cookie('MOD_AUTH_CAS_S', '', expires=0)
        resp.set_cookie('MOD_AUTH_CAS', '', expires=0)
        return resp
