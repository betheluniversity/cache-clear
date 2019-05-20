# Globals
import hashlib
import re
import subprocess

from app import app
from app.controllers.rpapi import rpapi_call


def clear_image_cache(image_path):
    # /academics/faculty/images/lundberg-kelsey.jpg"
    # Make sure image path starts with a slash
    if not image_path.startswith('/'):
        image_path = '/%s' % image_path

    resp = []

    def path_on_filesystem(path):
        path = re.sub(":", "%3A", path)
        digest = hashlib.sha1(path.encode('utf-8')).hexdigest()
        return "%s/%s/%s" % (
            app.config['THUMBOR_STORAGE_LOCATION'].rstrip('/'),
            digest[:2],
            digest[2:]
        )

    # 1. Remove the non-resized version from Varnish's cache
    rpapi_call('purge', host='www.bethel.edu', path=image_path)

    # 2. Remove any variant of the non-resized image that may be downloaded and stored in Thumbor
    for prefix in ['http://www.bethel.edu', 'https://www.bethel.edu',
                   'http://staging.bethel.edu', 'https://staging.bethel.edu']:
        path = prefix + image_path
        resp.append(path)
        encrypted_path = path_on_filesystem(path)
        resp.append(encrypted_path)

        # remove the file at the path
        subprocess.call(['rm', encrypted_path])

    # 3. Find any resized versions of the old image stored in Thumbor
    # 4. Remove the cached versions in Varnish without fetching new versions yet
    # 5. Remove the locally-stored resized versions stored in Thumbor
    cmd = 'find %s -wholename "*/smart/*%s"' % (app.config['THUMBOR_RESULT_STORAGE_LOCATION'], image_path)
    sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    results = sp.communicate()[0].split()

    matches = ""

    for result_path in results:
        url_params = re.compile(r'.+?/unsafe/(.+?)/smart/(http.+)').search(result_path)
        cached_path = '/resize/unsafe/%s/smart/%s' % (url_params.group(1), url_params.group(2))
        # Varnish caches all traffic to cdn[1-4] as cdn.bethel.edu
        rpapi_call('purge', host='cdn.bethel.edu', path=cached_path)
        sp2 = subprocess.Popen('rm ' + result_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # response = subprocess.call(['rm', result_path])
        response = sp2.communicate()
        if response == ('', ''):
            matches += "Deleted resize at \"%s\"\n" % result_path
        else:
            matches += "ERROR: Couldn't delete resize at \"%s\": \"%s\"\n" % (result_path, response[0])

    matches += "\n"

    # this iterates through resp two items at a time
    for x, y in zip(*[iter(resp)] * 2):
        matches += "Deleted original of \"%s\" at \n\"%s\"\n" % (str(x), str(y))

    return matches
