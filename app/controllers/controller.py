# Globals
import fnmatch
import hashlib
import base64
import os
import thumbor.storages as storages
from subprocess import call
from Crypto.Cipher import AES

from app import app


def clear_image_cache(image_path):
    # /academics/faculty/images/lundberg-kelsey.jpg"
    # Make sure image path starts with a slash
    if not image_path.startswith('/'):
        image_path = '/%s' % image_path

    resp = []

    def pad(s):
        return s + (16 - len(s) % 16) * "{"

    def path_on_filesystem(self, path):
        digest = hashlib.sha1(path.encode('utf-8')).hexdigest()
        return "%s/%s/%s" % (
            app.config['THUMBOR_RESULT_STORAGE_LOCATION'].rstrip('/'),
            digest[:2],
            digest[2:]
        )

    # for prefix in ['http://www.bethel.edu', 'https://www.bethel.edu',
    #                'http://staging.bethel.edu', 'https://staging.bethel.edu',
    #                'http://thumbor.bethel.edu', 'https://thumbor.bethel.edu']:
    path = image_path
    resp.append(path)
    encrypted_path = path_on_filesystem(path)
    resp.append(encrypted_path)

    # remove the file at the path
    # call(['rm', path])

    # now the result storage
    # file_name = image_path.split('/')[-1]
    # matches = []
    # for root, dirnames, filenames in os.walk(app.config['THUMBOR_RESULT_STORAGE_LOCATION']):
    #     for filename in fnmatch.filter(filenames, file_name):
    #         matches.append(os.path.join(root, filename))
    # for match in matches:
    #     call(['rm', match])

    # matches.extend(resp)

    return str(resp)
