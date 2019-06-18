# Imports from Python global packages
import re
import time

# Imports from packages installed from requirements.txt
import ldap
from flask import make_response, redirect, render_template, request, session, abort
from flask_classy import FlaskView, route

# Imports from elsewhere in this project
from app import app


class HomeView(FlaskView):

    # Extracted and adapted from MyBethel's _is_user_in_iam_groups() method
    def _load_ldap_groups(self):
        try:
            con = ldap.initialize(app.config['LDAP_CONNECTION_INFO'])
            con.simple_bind_s('BU\\svc-tinker', app.config['LDAP_SVC_TINKER_PASSWORD'])

            # code to get all users in a group
            raw_results = con.search_s('ou=Bethel Users,dc=bu,dc=ac,dc=bethel,dc=edu', ldap.SCOPE_SUBTREE,
                                       "(|(&(sAMAccountName=%s)))" % session['username'])

            groups = []
            for result in raw_results:
                for ldap_string in result[1]['memberOf']:
                    groups.append(re.search('CN=([^,]*)', ldap_string).group(1))

            return groups
        except:
            return []

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

        if 'user_groups' not in session.keys():
            session['user_groups'] = self._load_ldap_groups()

        # Only let members of these IAM Groups use cache-clear; everyone else will be denied with a 403
        authorized_groups = set(['CommMktg - Student Workers', 'CommMktg - Employees',
                                 'ITS-WebServicesStudents', 'ITS - WebServices'])
        if len(authorized_groups.intersection(set(session['user_groups']))) == 0:
            return abort(403)

    def index(self):
        print('before request')
        return render_template('index.html')

    @route('/favicon.ico')
    def favicon(self):
        print('favicon')
        return redirect('/static/images/favicon.ico')

    def logout(self):
        session.clear()
        resp = make_response(redirect(app.config['LOGOUT_URL']))
        resp.set_cookie('MOD_AUTH_CAS_S', '', expires=0)
        resp.set_cookie('MOD_AUTH_CAS', '', expires=0)
        return resp
