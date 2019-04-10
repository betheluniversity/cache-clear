import re

import requests
from requests.auth import HTTPBasicAuth

from app import app


def rpapi_call(action, host=None, url=None, advanced_ban_expression=None):
    api_destination = 'https://purge.bethel.edu/'
    authentication = HTTPBasicAuth(app.config['CASCADE_LOGIN']['username'], app.config['CASCADE_LOGIN']['password'])

    if action in ['purge', 'refresh'] and host is not None and url is not None:
        headers_to_send = {
            'API-Action': action,
            'Purge-Host': host,
            'Purge-URL': url
        }
    elif action == 'simple_ban' and host is not None and url is not None:
        headers_to_send = {
            'API-Action': 'ban',
            # TODO: when smart bans get enabled, change this to 'obj.http.x-host && obj.http.x-url'
            'Ban-Expression': 'req.http.host ~ %s && req.url ~ %s' % (host, url)
        }
    elif action == 'advanced_ban' and advanced_ban_expression is not None:
        """
        WARNING: currently there's no way for Varnish to do syntax checking on what it passes through to VCL.ban(),
        and ban() fails silently! If it gets passed a malformed expression, it will create it as a ban that is 
        already marked as "completed" (represented by 'C' in ban.list) and it will never be compared against the cache.
        This means that if the advanced_ban_expression passes our sanitization in this app, then RPAPI will always 
        return a 200 response and we won't be able to tell if it was valid or not without SSHing onto the Varnish 
        server and running `sudo varnishadm ban.list`.
        """
        headers_to_send = {
            'API-Action': 'ban',
            'Ban-Expression': advanced_ban_expression
        }
    else:
        return 'Invalid parameters'

    """
    Now that the request parameters have been constructed, send it to Varnish. If it receives a 200 response back,
    that means the action was successfully performed and Varnish should parrot back what it just did. Any other
    response status means that the action failed, but useful failure messages have not yet been implemented.
    """
    response = requests.get(api_destination, auth=authentication, headers=headers_to_send)
    response_content = re.compile(r'<body[^>]*>((.|[\n\r])*)</body>').search(response.content).group(1)

    return response_content
