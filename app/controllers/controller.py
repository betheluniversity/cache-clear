# Globals
import fnmatch
import hashlib
import re
import base64
import os
import subprocess

from app import app


def clear_image_cache(image_path):
    # /academics/faculty/images/lundberg-kelsey.jpg"
    # Make sure image path starts with a slash
    if not image_path.startswith('/'):
        image_path = '/%s' % image_path

    resp = []

    def pad(s):
        return s + (16 - len(s) % 16) * "{"

    def path_on_filesystem(path):
        path = re.sub("\:", "%3A", path)
        digest = hashlib.sha1(path.encode('utf-8')).hexdigest()
        return "%s/%s/%s" % (
            app.config['THUMBOR_STORAGE_LOCATION'].rstrip('/'),
            digest[:2],
            digest[2:]
        )


    for prefix in ['http://www.bethel.edu', 'https://www.bethel.edu',
                   'http://staging.bethel.edu', 'https://staging.bethel.edu']:
        path = prefix + image_path
        resp.append(path)
        encrypted_path = path_on_filesystem(path)
        resp.append(encrypted_path)

        # remove the file at the path
        subprocess.call(['rm', encrypted_path])

    # For local testing
    # cmd = 'find /Users/josiahtillman/Desktop -wholename "*/TestFolder/*"'
    cmd = 'find /opt/thumbor/resized_images/v2/un/sa/unsafe/ -wholename "*/smart/*' + image_path + '"'
    sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    results = sp.communicate()[0].split()

    for result_path in results:
        sp2 = subprocess.Popen('rm ' + result_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        response = sp2.stdout.readline()
        resp.append(response)
        # response = subprocess.call(['rm', result_path])
        response2 = sp2.communicate()[0].split()
        resp.append(response2)

    # # now the result storage
    # file_name = image_path.split('/')[-1]
    # matches = []
    # for root, dirnames, filenames in os.walk(app.config['THUMBOR_RESULT_STORAGE_LOCATION']):
    #     for filename in fnmatch.filter(filenames, file_name):
    #         matches.append(os.path.join(root, filename))
    # for match in matches:
    #     call(['rm', match])
    # matches.extend(resp)

    return str(resp)
